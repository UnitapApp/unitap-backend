from django.db import models
import uuid

from brightIDfaucet.settings import BRIGHT_ID_INTERFACE


class Chain(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    chain_id = models.CharField(max_length=255, unique=True)
    rpc_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.pk} - {self.symbol}:{self.chain_id}"


class BrightUser(models.Model):
    PENDING = "0"
    VERIFIED = "1"

    states = ((PENDING, "Pending"),
              (VERIFIED, "Verified"))

    address = models.CharField(max_length=45, unique=True)
    context_id = models.UUIDField(default=uuid.uuid4, unique=True)

    _verification_status = models.CharField(max_length=1, choices=states, default=PENDING)

    @property
    def verification_url(self, bright_driver=BRIGHT_ID_INTERFACE):
        return bright_driver.get_verification_link(str(self.context_id))

    @property
    def verification_status(self):
        return self.get_verification_status()

    @staticmethod
    def get_or_create(address):
        try:
            return BrightUser.objects.get(address=address)
        except BrightUser.DoesNotExist:
            return BrightUser.objects.create(address=address)

    def get_verification_status(self, bright_driver=BRIGHT_ID_INTERFACE) -> states:
        if self._verification_status == self.VERIFIED:
            return self.VERIFIED

        is_verified = bright_driver.get_verification_status(str(self.context_id))

        if is_verified:
            self._verification_status = self.VERIFIED
            self.save()

        return self._verification_status

    def get_verification_url(self, bright_driver=BRIGHT_ID_INTERFACE) -> str:
        return bright_driver.get_verification_link(str(self.context_id))


class ClaimReceipt(models.Model):
    chain = models.ForeignKey(Chain, related_name="claims", on_delete=models.PROTECT)
    bright_user = models.ForeignKey(BrightUser, related_name="claims", on_delete=models.PROTECT)

    amount = models.BigIntegerField()
    datetime = models.DateTimeField()
    tx_hash = models.CharField(max_length=100, blank=True, null=True)
