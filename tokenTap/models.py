from django.core.cache import cache
from django.db import models
from django.utils import timezone

from authentication.models import NetworkTypes, UserProfile
from core.models import UserConstraint
from faucet.models import Chain, ClaimReceipt

from .constraints import (
    OnceInALifeTimeVerification,
    OncePerMonthVerification,
    OptimismHasClaimedGasInThisRound,
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
    name = models.CharField(max_length=100)

    distributor = models.CharField(max_length=100, null=True, blank=True)
    distributor_url = models.URLField(max_length=255, null=True, blank=True)
    discord_url = models.URLField(max_length=255, null=True, blank=True)
    twitter_url = models.URLField(max_length=255, null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)
    token_image_url = models.URLField(max_length=255, null=True, blank=True)

    token = models.CharField(max_length=100)
    token_address = models.CharField(max_length=255)
    amount = models.BigIntegerField()
    chain = models.ForeignKey(Chain, on_delete=models.CASCADE, related_name="token_distribution")

    permissions = models.ManyToManyField(Constraint, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    max_number_of_claims = models.IntegerField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

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
    token_distribution = models.ForeignKey(TokenDistribution, on_delete=models.CASCADE, related_name="claims")
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="tokentap_claims")
    created_at = models.DateTimeField(auto_now_add=True, editable=True)

    notes = models.TextField(null=True, blank=True)

    signature = models.CharField(max_length=1024, blank=True, null=True)
    nonce = models.BigIntegerField(null=True, blank=True)

    status = models.CharField(max_length=30, choices=ClaimReceipt.states, default=ClaimReceipt.PENDING)

    tx_hash = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.token_distribution} - {self.user_profile}"

    @property
    def user(self):
        return self.user_profile.wallets.get(wallet_type=NetworkTypes.EVM).address

    @property
    def token(self):
        return self.token_distribution.token_address

    @property
    def amount(self):
        return self.token_distribution.amount

    @property
    def age(self):
        return timezone.now() - self.created_at
