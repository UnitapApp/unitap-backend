from django.db import models
from faucet.models import Chain
from django.utils import timezone
from authentication.models import NetworkTypes, UserProfile
from core.models import UserConstraint

# Create your models here.

class Constraint(UserConstraint):
    pass
    

class Raffle(models.Model):

    class Meta:
        models.UniqueConstraint(
            fields=['chain', 'contract', 'raffleId'], name="unique_raffle")

    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    contract = models.CharField(max_length=256)
    raffleId = models.BigIntegerField()
    creator = models.CharField(max_length=256, null=True, blank=True)
    creator_url = models.URLField(max_length=255, null=True, blank=True)
    discord_url = models.URLField(max_length=255, null=True, blank=True)
    twitter_url = models.URLField(max_length=255, null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)

    prize_amount = models.BigIntegerField()
    prize_asset = models.CharField(max_length=255)
    prize_name = models.CharField(max_length=100)
    prize_symbol = models.CharField(max_length=100)
    decimals = models.IntegerField(default=18)
    

    is_prize_nft = models.BooleanField(default=False)
    nft_id = models.BigIntegerField(null=True, blank=True)
    token_uri = models.TextField(null=True, blank=True)

    chain = models.ForeignKey(
        Chain, on_delete=models.CASCADE, related_name="raffles"
    )

    constraints = models.ManyToManyField(Constraint, blank=True, related_name="raffles")
    constraint_params = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    start_at = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField(null=True, blank=True)
    max_number_of_entries = models.IntegerField(null=True, blank=True)
    max_multiplier = models.IntegerField(default=1)

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
        return self.max_number_of_entries <= self.number_of_entries

    @property
    def is_claimable(self):
        return self.is_started and not self.is_expired and \
            not self.is_maxed_out and self.is_active

    @property
    def number_of_entries(self):
        return self.entries.count()
    
    @property
    def number_of_onchain_entries(self):
        return self.entries.filter(tx_hash__isnull=False).count()
    
    @property
    def winner(self):
        winner_entry = self.winner_entry
        if winner_entry:
            return winner_entry.user_profile
        
    @property
    def winner_entry(self):
        try:
            return self.entries.get(is_winner=True)
        except RaffleEntry.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.name}"


class RaffleEntry(models.Model):
    class Meta:
        unique_together = (("raffle", "user_profile"),)
        verbose_name_plural = "raffle entries"

    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name="entries")
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="raffle_entries"
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=True)

    multiplier = models.IntegerField(default=1)
    is_winner = models.BooleanField(blank=True, default=False)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)
    claiming_prize_tx = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.raffle} - {self.user_profile}"

    @property
    def user(self):
        return self.user_profile.wallets.get(wallet_type=NetworkTypes.EVM).address

    def save(self, *args, **kwargs):
        if self.is_winner:
            try:
                entry = RaffleEntry.objects.get(is_winner=True, raffle=self.raffle)
                assert entry.pk == self.pk, "The raffle already has a winner"
            except RaffleEntry.DoesNotExist:
                pass
                    
        super().save(*args, **kwargs)
