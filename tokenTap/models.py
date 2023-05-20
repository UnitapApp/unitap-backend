from django.utils import timezone
from django.db import models
from authentication.models import NetworkTypes, UserProfile
from faucet.models import Chain
from permissions.models import Permission


class TokenDistribution(models.Model):
    name = models.CharField(max_length=100)

    distributor = models.CharField(max_length=100)
    distributor_url = models.URLField(max_length=255, null=True, blank=True)
    discord_url = models.URLField(max_length=255, null=True, blank=True)
    twitter_url = models.URLField(max_length=255, null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)

    token = models.CharField(max_length=100)
    token_address = models.CharField(max_length=255)
    amount = models.BigIntegerField()
    chain = models.ForeignKey(
        Chain, on_delete=models.CASCADE, related_name="token_distribution"
    )

    permissions = models.ManyToManyField(Permission, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    max_number_of_claims = models.IntegerField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

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
        return not self.is_expired and not self.is_maxed_out

    def __str__(self):
        return f"{self.name} - {self.token} - {self.amount}"


class TokenDistributionClaim(models.Model):
    token_distribution = models.ForeignKey(
        TokenDistribution, on_delete=models.CASCADE, related_name="claims"
    )
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="tokentap_claims"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(null=True, blank=True)

    signature = models.CharField(max_length=1024, blank=True, null=True)
    nonce = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.token_distribution} - {self.user_profile}"

    @property
    def payload(self):
        m = {
            "user": self.user_profile.wallets.get(wallet_type=NetworkTypes.EVM).address,
            "token": self.token_distribution.token_address,
            "amount": self.token_distribution.amount,
            "nonce": self.nonce,
            "signature": self.signature,
        }
        return m

    @property
    def user(self):
        return self.user_profile.wallets.get(wallet_type=NetworkTypes.EVM).address

    @property
    def token(self):
        return self.token_distribution.token_address

    @property
    def amount(self):
        return self.token_distribution.amount
