import uuid

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from safedelete.models import SafeDeleteModel
from web3 import Web3

# from authentication.helpers import BRIGHTID_SOULDBOUND_INTERFACE
from authentication.thirdpartydrivers import (
    BaseThirdPartyDriver,
    BrightIDConnectionDriver,
    ENSDriver,
    FarcasterDriver,
    GitcoinPassportDriver,
    LensDriver,
    TwitterDriver,
)
from core.models import NetworkTypes
from core.thirdpartyapp import Subgraph


class ProfileManager(models.Manager):
    def get_or_create(self, first_context_id):
        try:
            return super().get_queryset().get(initial_context_id=first_context_id)
        except UserProfile.DoesNotExist:
            _user = User.objects.create_user(username=first_context_id)
            _profile = UserProfile(user=_user, initial_context_id=first_context_id)
            _profile.save()
            return _profile

    def get_by_wallet_address(self, wallet_address):
        try:
            return Wallet.objects.get(
                address=Web3.to_checksum_address(wallet_address)
            ).user_profile
        except Wallet.DoesNotExist:
            return None

    def create_with_wallet_address(self, wallet_address):
        _user = User.objects.create_user(username="UNT" + str(uuid.uuid4())[:16])
        _profile = UserProfile.objects.create(user=_user)
        Wallet.objects.create(
            wallet_type=NetworkTypes.EVM,  # TODO support register with non evms
            user_profile=_profile,
            address=Web3.to_checksum_address(wallet_address),
        )
        _profile.username = f"User{_profile.pk}"
        _profile.save()
        return _profile

    def get_or_create_with_wallet_address(self, wallet_address):
        try:
            profile = Wallet.objects.get(
                address=Web3.to_checksum_address(wallet_address)
            ).user_profile
            if profile.username is None:
                profile.username = f"User{profile.pk}"
                profile.save()
            return profile
        except Wallet.DoesNotExist:
            return self.create_with_wallet_address(wallet_address)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="profile")
    initial_context_id = models.CharField(
        max_length=512, unique=True, null=True, blank=True
    )

    username = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Username can only contain letters, digits and @/./+/-/_.",
            ),
        ],
        null=True,
        blank=True,
        unique=True,
    )

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    prizetap_winning_chance_number = models.IntegerField(
        default=0, blank=False, null=False, validators=(MinValueValidator(0),)
    )

    objects = ProfileManager()

    @property
    def age(self):
        if self.created_at is None:
            return -1
        return timezone.now() - self.created_at

    @property
    def is_meet_verified(self):
        try:
            bo = BrightIDConnection.get_connection(self)
            return bo.is_meets_verified
        except:  # noqa E722
            return False

    @property
    def is_aura_verified(self):
        return False

    def owns_wallet(self, wallet_address):
        return self.wallets.filter(address=wallet_address).exists()

    def has_unitap_pass(self):
        sub = Subgraph()
        addresses = Wallet.objects.filter(user_profile__pk=self.pk).values_list(
            "address", flat=True
        )
        if not addresses:
            return False, list()
        owners = sub.get_unitap_pass_holders(addresses=addresses)
        return (
            bool(owners),
            [token_id for _, token_ids in owners.items() for token_id in token_ids],
        )

    def __str__(self) -> str:
        return self.username if self.username else f"User{self.pk}"

    @staticmethod
    def user_count():
        cached_user_count = cache.get("user_profile_count")
        if cached_user_count:
            return cached_user_count
        count = UserProfile.objects.count()
        cache.set("user_profile_count", count, 300)
        return count

    def get_all_thirdparty_connections(self):
        connections = []

        # Loop through each related connection
        for rel in self._meta.get_fields():
            if rel.one_to_many and issubclass(
                rel.related_model, BaseThirdPartyConnection
            ):
                related_manager = getattr(self, rel.get_accessor_name())
                connections.extend(related_manager.all())

        return connections


class Wallet(SafeDeleteModel):
    wallet_type = models.CharField(choices=NetworkTypes.networks, max_length=10)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.PROTECT, related_name="wallets"
    )
    address = models.CharField(max_length=512, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("address"),
                "wallet_type",
                name="unique_wallet_address",
            ),
        ]

    def __str__(self):
        return f"{self.wallet_type} Wallet for {self.user_profile.username}"


class BaseThirdPartyConnection(models.Model):
    title = "BaseThirdPartyConnection"
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.PROTECT, related_name="%(class)s"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    driver = BaseThirdPartyDriver()

    class Meta:
        abstract = True

    def is_connected(self):
        return bool(self.created_at)

    @classmethod
    def get_connection(cls, user_profile):
        return cls.objects.get(user_profile=user_profile)


class BrightIDConnection(BaseThirdPartyConnection):
    title = "BrightID"
    context_id = models.CharField(max_length=512, unique=True)

    driver = BrightIDConnectionDriver()

    @property
    def age(self):
        return timezone.now() - self.created_at

    @property
    def is_meets_verified(self):
        is_verified, status = self.driver.get_meets_verification_status(self.context_id)
        return is_verified

    @property
    def is_aura_verified(self):
        return False
        return self.driver.get_aura_verification_status(self.context_id)


class GitcoinPassportSaveError(Exception):
    pass


class GitcoinPassportConnection(BaseThirdPartyConnection):
    title = "GitcoinPassport"
    user_wallet_address = models.CharField(max_length=255)
    driver = GitcoinPassportDriver()

    @property
    def score(self):
        score_tuple = self.driver.get_score(self.user_wallet_address)
        return score_tuple[0] if score_tuple else 0.0


@receiver(pre_save, sender=GitcoinPassportConnection)
def submit_passport(sender, instance: GitcoinPassportConnection, **kwargs):
    if instance.pk is not None:
        return
    res = instance.driver.submit_passport(instance.user_wallet_address)
    if res is None:
        raise GitcoinPassportSaveError(
            "Something went wrong in connection to gitcoin passport server"
        )
    if res == "0":
        raise GitcoinPassportSaveError("Gitcoin passport not exists.")


class TwitterConnection(BaseThirdPartyConnection):
    title = "Twitter"
    oauth_token = models.CharField(max_length=255, unique=True, blank=False, null=False)
    oauth_token_secret = models.CharField(
        max_length=255, unique=True, blank=False, null=False
    )
    access_token = models.CharField(max_length=255, unique=True, blank=True, null=True)
    access_token_secret = models.CharField(
        max_length=255, unique=True, blank=True, null=True
    )
    driver = TwitterDriver()

    def is_connected(self):
        return bool(self.access_token and self.access_token_secret)

    @property
    def tweet_count(self):
        return self.driver.get_tweet_count(self.access_token, self.access_token_secret)

    @property
    def follower_count(self):
        return self.driver.get_follower_count(
            self.access_token, self.access_token_secret
        )

    def is_replied(self, self_tweet_id, target_tweet_id):
        return self.driver.get_is_replied(
            self.access_token, self.access_token_secret, self_tweet_id, target_tweet_id
        )

    def is_liked(self, target_tweet_id):
        return self.driver.get_is_liked(
            self.access_token, self.access_token_secret, target_tweet_id
        )


class ENSConnection(BaseThirdPartyConnection):
    title = "ENS"
    user_wallet_address = models.CharField(max_length=255)
    driver = ENSDriver()

    @property
    def name(self):
        return self.driver.get_name(self.user_wallet_address)

    def is_connected(self):
        return bool(self.name)


class FarcasterConnection(BaseThirdPartyConnection):
    title = "Farcaster"
    user_wallet_address = models.CharField(max_length=255)
    driver = FarcasterDriver()

    @property
    def fid(self):
        return self.driver.get_fid(self.user_wallet_address)

    def is_connected(self):
        return bool(self.fid)


class FarcasterSaveError(Exception):
    pass


@receiver(pre_save, sender=FarcasterConnection)
def check_farcaster_profile_existance(sender, instance: FarcasterConnection, **kwargs):
    if instance.pk is not None:
        return
    res = instance.fid
    if res is None:
        raise FarcasterSaveError("Farcaster profile for this wallet not found.")


class LensConnection(BaseThirdPartyConnection):
    title = "Lens"
    user_wallet_address = models.CharField(max_length=255)
    driver = LensDriver()

    @property
    def profile_id(self):
        return self.driver.get_profile_id(self.user_wallet_address)

    def is_connected(self):
        return bool(self.profile_id)


class LensSaveError(Exception):
    pass


@receiver(pre_save, sender=LensConnection)
def check_lens_profile_existance(sender, instance: LensConnection, **kwargs):
    if instance.pk is not None:
        return
    res = instance.profile_id
    if res is None:
        raise FarcasterSaveError("Lens profile for this wallet not found.")
