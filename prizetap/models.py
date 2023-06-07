from django.db import models
from faucet.models import Chain
from django.utils import timezone
from authentication.models import NetworkTypes, UserProfile

# Create your models here.


class Raffle(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    creator = models.CharField(max_length=256, null=True, blank=True)
    creator_url = models.URLField(max_length=255, null=True, blank=True)
    discord_url = models.URLField(max_length=255, null=True, blank=True)
    twitter_url = models.URLField(max_length=255, null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)

    prize = models.CharField(max_length=100)

    chain = models.ForeignKey(
        Chain, on_delete=models.CASCADE, related_name="raffles", null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    deadline = models.DateTimeField(null=True, blank=True)
    max_number_of_entries = models.IntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    winner = models.CharField(max_length=1024, null=True, blank=True)

    @property
    def is_expired(self):
        if self.deadline is None:
            return False
        return self.deadline < timezone.now()

    @property
    def is_maxed_out(self):
        if self.max_number_of_entries is None:
            return False
        return self.max_number_of_entries <= self.entries.count()

    @property
    def is_claimable(self):
        return not self.is_expired and not self.is_maxed_out and self.is_active

    def __str__(self):
        return f"{self.name} - {self.prize}"


class RaffleEntry(models.Model):
    class Meta:
        unique_together = (("raffle", "user_profile"),)

    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name="entries")
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="raffle_entries"
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=True)

    signature = models.CharField(max_length=1024, blank=True, null=True)
    nonce = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.raffle} - {self.user_profile}"

    @property
    def user(self):
        return self.user_profile.wallets.get(wallet_type=NetworkTypes.EVM).address
