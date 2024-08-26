from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from authentication.models import UserProfile
from core.models import BigNumField, Chain, UserConstraint
from faucet.constraints import OptimismClaimingGasConstraint, OptimismDonationConstraint
from cloudflare_images.field import CloudflareImagesField

from .constraints import HaveUnitapPass, NotHaveUnitapPass


class Constraint(UserConstraint):
    constraints = UserConstraint.constraints + [
        HaveUnitapPass,
        NotHaveUnitapPass,
        OptimismDonationConstraint,
        OptimismClaimingGasConstraint,
    ]
    name = UserConstraint.create_name_field(constraints)


class Raffle(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        REJECTED = "REJECTED", _("Rejected")
        VERIFIED = "VERIFIED", _("Verified")
        RANDOM_WORDS_SET = "RWS", _("Random words are set")
        WINNERS_SET = "WS", _("Winners are set")
        CLOSED = "CLOSED", _("Closed")

    class Meta:
        models.UniqueConstraint(
            fields=["chain", "contract", "raffleId"], name="unique_raffle"
        )

    name = models.CharField(max_length=256)
    description = models.TextField()
    necessary_information = models.TextField(null=True, blank=True)
    contract = models.CharField(max_length=256)
    raffleId = models.BigIntegerField(null=True, blank=True)
    creator_name = models.CharField(max_length=255)
    creator_profile = models.ForeignKey(
        UserProfile, on_delete=models.DO_NOTHING, related_name="raffles"
    )
    creator_address = models.CharField(max_length=255)
    creator_url = models.URLField(max_length=255, null=True, blank=True)
    discord_url = models.URLField(max_length=255, null=True, blank=True)
    twitter_url = models.URLField(max_length=255, null=True, blank=True)
    email_url = models.EmailField(max_length=255)
    telegram_url = models.URLField(max_length=255, null=True, blank=True)
    image = CloudflareImagesField(max_length=255, null=True, blank=True)

    prize_amount = BigNumField()
    prize_asset = models.CharField(max_length=255)
    prize_name = models.CharField(max_length=100)
    prize_symbol = models.CharField(max_length=100)
    decimals = models.IntegerField(default=18)

    is_prize_nft = models.BooleanField(default=False)
    nft_ids = models.TextField(null=True, blank=True)
    token_uri = models.TextField(null=True, blank=True)

    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, related_name="raffles")

    constraints = models.ManyToManyField(Constraint, blank=True, related_name="raffles")
    constraint_params = models.TextField(null=True, blank=True)
    reversed_constraints = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    start_at = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()
    max_number_of_entries = models.IntegerField(validators=[MinValueValidator(1)])
    max_multiplier = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    winners_count = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    pre_enrollment_file = models.FileField(
        upload_to="prizetap/pre_enrollments/%Y/%m/%d",
        validators=[FileExtensionValidator(allowed_extensions=["csv"])],
        blank=True,
        null=True,
    )
    pre_enrollment_wallets = models.TextField(
        blank=True,
        null=True,
    )
    is_processed = models.BooleanField(default=False)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    rejection_reason = models.TextField(null=True, blank=True)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)
    vrf_tx_hash = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    @property
    def is_started(self):
        return timezone.now() >= self.start_at

    @property
    def is_expired(self):
        if self.deadline is None:
            return False
        return self.deadline < timezone.now()

    @property
    def is_maxed_out(self):
        if self.max_number_of_entries is None:
            return False
        return self.max_number_of_entries <= self.number_of_onchain_entries

    @property
    def is_claimable(self):
        return (
            self.status == self.Status.VERIFIED
            and self.is_started
            and not self.is_expired
            and not self.is_maxed_out
            and self.is_active
            and not self.pre_enrollment_wallets
        )

    @property
    def number_of_entries(self):
        return self.entries.count()

    @property
    def number_of_onchain_entries(self):
        return self.entries.filter(tx_hash__isnull=False).count()

    @property
    def winners(self):
        winner_entries = self.winner_entries
        if winner_entries:
            return [e.user_profile for e in winner_entries]

    @property
    def winner_entries(self):
        return self.entries.filter(is_winner=True)

    @property
    def reversed_constraints_list(self):
        return self.reversed_constraints.split(",") if self.reversed_constraints else []

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.VERIFIED and not self.raffleId:
            raise Exception("The raffleId of a verified raffle can't be empty")

        super().save(*args, **kwargs)


class RaffleEntry(models.Model):
    class Meta:
        unique_together = (("raffle", "user_profile"),)
        verbose_name_plural = "raffle entries"

    raffle = models.ForeignKey(Raffle, on_delete=models.PROTECT, related_name="entries")
    user_profile = models.ForeignKey(
        UserProfile,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="raffle_entries",
    )

    user_wallet_address = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True, editable=True)

    multiplier = models.IntegerField(default=1)
    is_winner = models.BooleanField(blank=True, default=False)
    pre_enrollment = models.BooleanField(blank=True, default=False)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)
    claiming_prize_tx = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.raffle} - {self.user_profile}"

    @property
    def age(self):
        return timezone.now() - self.created_at

    @classmethod
    def set_entry_user_profiles(cls, user):
        user_profile: UserProfile = user.profile
        with transaction.atomic():
            user_wallets = list(user_profile.wallets.values_list("address", flat=True))
            entities = RaffleEntry.objects.filter(
                user_wallet_address__in=user_wallets
            ).all()
            for e in entities:
                e.user_profile = user_profile

            RaffleEntry.objects.bulk_update(entities, ["user_profile"])


class LineaRaffleEntries(models.Model):
    wallet_address = models.CharField(max_length=255)
    raffle = models.ForeignKey(
        Raffle, on_delete=models.CASCADE, related_name="linea_entries"
    )
    is_winner = models.BooleanField(blank=True, default=False)
    claim_tx = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.wallet_address)
