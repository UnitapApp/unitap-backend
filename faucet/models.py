from datetime import datetime, timedelta
from django.db import models
import uuid
from django.utils import timezone
from encrypted_model_fields.fields import EncryptedCharField
import binascii
from bip_utils import Bip44Coins, Bip44
from web3.exceptions import TimeExhausted

from brightIDfaucet.settings import BRIGHT_ID_INTERFACE

# import django transaction
from django.db import transaction


class WalletAccount(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    private_key = EncryptedCharField(max_length=100)

    @property
    def address(self):
        node = Bip44.FromPrivateKey(
            binascii.unhexlify(self.private_key), Bip44Coins.ETHEREUM
        )
        return node.PublicKey().ToAddress()

    def __str__(self) -> str:
        return "%s - %s" % (self.name, self.address)

    @property
    def main_key(self):
        return self.private_key


class BrightUserManager(models.Manager):
    def get_or_create(self, address):
        try:
            return super().get_queryset().get(address=address)
        except BrightUser.DoesNotExist:
            _user = BrightUser(address=address, _sponsored=True)

            # don't create user if sponsorship fails
            # so user can retry connecting their wallet
            if BRIGHT_ID_INTERFACE.sponsor(str(_user.context_id)):
                _user.save()
                return _user


class BrightUser(models.Model):
    PENDING = "0"
    VERIFIED = "1"

    states = ((PENDING, "Pending"), (VERIFIED, "Verified"))

    address = models.CharField(max_length=45, unique=True)
    context_id = models.UUIDField(default=uuid.uuid4, unique=True)

    _verification_status = models.CharField(
        max_length=1, choices=states, default=PENDING
    )
    _last_verified_datetime = models.DateTimeField(
        default=timezone.make_aware(datetime.utcfromtimestamp(0))
    )
    _sponsored = models.BooleanField(default=False)

    objects = BrightUserManager()

    def __str__(self):
        return "%d - %s" % (self.pk, self.address)

    @property
    def verification_url(self, bright_interface=BRIGHT_ID_INTERFACE):
        return bright_interface.get_verification_link(str(self.context_id))

    @property
    def verification_status(self):
        _now = timezone.now()
        _delta = _now - self._last_verified_datetime
        _max_delta = timedelta(days=7)

        if self._verification_status == self.VERIFIED and _delta <= _max_delta:
            return self.VERIFIED
        return self.get_verification_status()

    def get_verification_status(self) -> states:
        is_verified = BRIGHT_ID_INTERFACE.get_verification_status(str(self.context_id))
        if is_verified:
            self._verification_status = self.VERIFIED
            self._last_verified_datetime = timezone.now()
        else:
            self._verification_status = self.PENDING
        self.save()
        return self._verification_status

    def get_verification_url(self) -> str:
        return BRIGHT_ID_INTERFACE.get_verification_link(str(self.context_id))


class ClaimReceipt(models.Model):
    MAX_PENDING_DURATION = 15  # minutes
    PENDING = "0"
    VERIFIED = "1"
    REJECTED = "2"
    UPDATING = "3"

    states = (
        (PENDING, "Pending"),
        (VERIFIED, "Verified"),
        (REJECTED, "Rejected"),
        (UPDATING, "Updating"),
    )

    chain = models.ForeignKey("Chain", related_name="claims", on_delete=models.PROTECT)
    bright_user = models.ForeignKey(
        BrightUser, related_name="claims", on_delete=models.PROTECT
    )

    _status = models.CharField(max_length=1, choices=states, default=PENDING)

    amount = models.BigIntegerField()
    datetime = models.DateTimeField()
    tx_hash = models.CharField(max_length=100, blank=True, null=True)

    def is_expired(self):
        return timezone.now() - self.datetime > timedelta(
            minutes=self.MAX_PENDING_DURATION
        )

    def _verified_or_rejected(self):
        return self._status in [self.VERIFIED, self.REJECTED]

    def _has_tx_hash(self):
        return self.tx_hash is not None

    def status(self):
        if not self._verified_or_rejected():
            self.update_status()
        return self._status

    def update_status(self):
        with transaction.atomic():
            _self = ClaimReceipt.objects.select_for_update().get(pk=self.pk)
            if _self._state == self.UPDATING:
                return

            _current_status = _self._status
            _self._status = self.UPDATING
            _self.save()

        if _self._has_tx_hash():
            try:
                from faucet.faucet_manager.fund_manager import EVMFundManager

                if EVMFundManager(_self.chain).is_tx_verified(_self.tx_hash):
                    _self._status = ClaimReceipt.VERIFIED
                else:
                    _self._status = ClaimReceipt.REJECTED
            except TimeExhausted:
                if _self.is_expired():
                    _self._status = ClaimReceipt.REJECTED
        elif _self.is_expired():
            _self._status = ClaimReceipt.REJECTED

        # remove updating status if it's still there
        if _self._status == self.UPDATING:
            _self._status = _current_status

        _self.save()


class Chain(models.Model):
    chain_name = models.CharField(max_length=255)
    chain_id = models.CharField(max_length=255, unique=True)

    native_currency_name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    decimals = models.IntegerField(default=18)

    explorer_url = models.URLField(max_length=255, blank=True, null=True)
    rpc_url = models.URLField(max_length=255, blank=True, null=True)
    logo_url = models.URLField(max_length=255, blank=True, null=True)
    rpc_url_private = models.URLField(max_length=255)

    max_claim_amount = models.BigIntegerField()

    poa = models.BooleanField(default=False)

    fund_manager_address = models.CharField(max_length=255)
    wallet = models.ForeignKey(
        WalletAccount, related_name="chains", on_delete=models.PROTECT
    )

    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.pk} - {self.symbol}:{self.chain_id}"


class GlobalSettings(models.Model):
    weekly_chain_claim_limit = models.IntegerField(default=10)
