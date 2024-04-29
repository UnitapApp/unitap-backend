import uuid

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from safedelete.models import SafeDeleteModel

# from authentication.helpers import BRIGHTID_SOULDBOUND_INTERFACE
from authentication.thirdpartydrivers import (
    BaseThirdPartyDriver,
    BrightIDConnectionDriver,
    GitcoinPassportDriver,
    TwitterDriver,
)
from core.models import NetworkTypes


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
            return Wallet.objects.get(address=wallet_address).user_profile
        except Wallet.DoesNotExist:
            return None

    def create_with_wallet_address(self, wallet_address):
        _user = User.objects.create_user(username="UNT" + str(uuid.uuid4())[:16])
        _profile = UserProfile.objects.create(user=_user)
        Wallet.objects.create(
            wallet_type=NetworkTypes.EVM,  # TODO support register with non evms
            user_profile=_profile,
            address=wallet_address,
        )
        _profile.username = f"User{_profile.pk}"
        _profile.save()
        return _profile

    def get_or_create_with_wallet_address(self, wallet_address):
        try:
            profile = Wallet.objects.get(address=wallet_address).user_profile
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

    @property
    def is_connected_to_brightid(self):
        return BrightIDConnection.is_connected(self)

    def owns_wallet(self, wallet_address):
        return self.wallets.filter(address=wallet_address).exists()

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
                if isinstance(rel.related_model, TwitterConnection):
                    connections.extend(related_manager.filter(access_key__isnull=False))
                    continue

                connections.extend(related_manager.all())

        return connections


class Wallet(SafeDeleteModel):
    wallet_type = models.CharField(choices=NetworkTypes.networks, max_length=10)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.PROTECT, related_name="wallets"
    )
    address = models.CharField(max_length=512)
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

    @classmethod
    def is_connected(cls, user_profile):
        return cls.objects.filter(user_profile=user_profile).exists()

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
        return self.driver.get_score(self.user_wallet_address)[0]


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
    access_token = models.CharField(
        max_length=255, unique=True, blank=False, null=False
    )
    access_token_secret = models.CharField(
        max_length=255, unique=True, blank=False, null=False
    )
    driver = TwitterDriver()
