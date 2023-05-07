from django.utils import timezone
from django.db import models

from faucet.models import Chain

# Create your models here.


class TokenDistribution(models.Model):
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    token_address = models.CharField(max_length=255)
    amount = models.BigIntegerField()
    chain = models.ForeignKey(
        Chain, on_delete=models.CASCADE, related_name="token_distribution"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    @property
    def is_expired(self):
        if self.deadline is None:
            return False
        return self.deadline < timezone.now()
