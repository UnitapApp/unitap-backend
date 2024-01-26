from django.core.cache import cache
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from authentication.models import UserProfile
from core.models import Chain, UserConstraint
from faucet.constraints import OptimismHasClaimedGasInThisRound
from faucet.models import ClaimReceipt

from .constraints import (
    OnceInALifeTimeVerification,
    OncePerMonthVerification,
    TimeUtils,
)


class Constraint(UserConstraint):
    constraints = UserConstraint.constraints + [
        OncePerMonthVerification,
        OnceInALifeTimeVerification,
        OptimismHasClaimedGasInThisRound,
    ]
    name = UserConstraint.create_name_field(constraints)


class TokenDistribution(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        REJECTED = "REJECTED", _("Rejected")
        VERIFIED = "VERIFIED", _("Verified")

    name = models.CharField(max_length=255)

    distributor = models.CharField(max_length=255, null=True)
    distributor_profile = models.ForeignKey(
        UserProfile, on_delete=models.DO_NOTHING, related_name="token_distributions"
    )
    distributor_address = models.CharField(max_length=255)
    distributor_url = models.URLField(max_length=255, null=True, blank=True)
    discord_url = models.URLField(max_length=255, null=True, blank=True)
    twitter_url = models.URLField(max_length=255, null=True, blank=True)
    email_url = models.EmailField(max_length=255)
    telegram_url = models.URLField(max_length=255, null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)
    token_image_url = models.URLField(max_length=255, null=True, blank=True)

    token = models.CharField(max_length=100)
    token_address = models.CharField(max_length=255)
    amount = models.CharField(max_length=100)
    chain = models.ForeignKey(
        Chain, on_delete=models.CASCADE, related_name="token_distribution"
    )
    contract = models.CharField(max_length=255, null=True, blank=True)

    constraints = models.ManyToManyField(
        Constraint, blank=True, related_name="token_distributions"
    )
    constraint_params = models.TextField(null=True, blank=True)
    reversed_constraints = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    start_at = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()

    max_number_of_claims = models.PositiveIntegerField(
        null=True, validators=[MinValueValidator(1)]
    )

    notes = models.TextField()
    necessary_information = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    rejection_reason = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    @property
    def reversed_constraints_list(self):
        return self.reversed_constraints.split(",") if self.reversed_constraints else []

    @property
    def is_expired(self):
        if self.deadline is None:
            return False
        return self.deadline < timezone.now()

    @property
    def is_maxed_out(self):
        if self.max_number_of_claims is None:
            return False
        return self.max_number_of_claims <= self.claims.count()

    @property
    def is_claimable(self):
        return not self.is_expired and not self.is_maxed_out and self.is_active

    @property
    def number_of_claims(self):
        return self.claims.count()

    @property
    def total_claims_since_last_round(self):
        cached_total_claims_since_last_round = cache.get(
            f"token_tap_token_distribution_total_claims_since_last_round_{self.pk}"
        )
        if cached_total_claims_since_last_round:
            return cached_total_claims_since_last_round

        total_claims_since_last_round = TokenDistributionClaim.objects.filter(
            token_distribution=self,
            created_at__gte=TimeUtils.get_first_day_of_last_month(),
            status__in=[ClaimReceipt.VERIFIED, ClaimReceipt.PENDING],
        ).count()
        cache.set(
            f"token_tap_token_distribution_total_claims_since_last_round_{self.pk}",
            total_claims_since_last_round,
            300,
        )
        return total_claims_since_last_round

    def __str__(self):
        return f"{self.name} - {self.token} - {self.amount}"


class TokenDistributionClaim(models.Model):
    token_distribution = models.ForeignKey(
        TokenDistribution, on_delete=models.CASCADE, related_name="claims"
    )
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="tokentap_claims"
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=True)

    user_wallet_address = models.CharField(max_length=255, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    signature = models.CharField(max_length=1024, blank=True, null=True)
    nonce = models.BigIntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=30, choices=ClaimReceipt.states, default=ClaimReceipt.PENDING
    )

    tx_hash = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.token_distribution} - {self.user_profile}"

    @property
    def token(self):
        return self.token_distribution.token_address

    @property
    def amount(self):
        return self.token_distribution.amount

    @property
    def age(self):
        return timezone.now() - self.created_at


class GlobalSettings(models.Model):
    index = models.CharField(max_length=255, unique=True)
    value = models.TextField()

    @classmethod
    def set(cls, index: str, value: str):
        return cls.objects.update_or_create(index=index, defaults={"value": value})

    @classmethod
    def get(cls, index: str, default: str = None):
        try:
            return cls.objects.get(index=index).value
        except cls.DoesNotExist as e:
            if default is not None:
                obj, _ = cls.set(index, default)
                return obj.value
            raise e
