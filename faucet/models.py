from datetime import datetime, timedelta
from django.db import models
import uuid
from django.utils import timezone
from encrypted_model_fields.fields import EncryptedCharField
import binascii
from bip_utils import Bip44Coins, Bip44
from web3.exceptions import TimeExhausted
from django.conf import settings
from authentication.models import NetworkTypes, UserProfile, Wallet

from brightIDfaucet.settings import BRIGHT_ID_INTERFACE

# import django transaction
from django.db import transaction


class WalletAccount(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    private_key = EncryptedCharField(max_length=100)

    @property
    def address(self):
        try:
            node = Bip44.FromPrivateKey(
                binascii.unhexlify(self.private_key), Bip44Coins.ETHEREUM
            )
            return node.PublicKey().ToAddress()
        except:
            pass

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

            # if it's debug save the object
            if settings.DEBUG:
                _user.save()
                return _user

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
    PENDING = "Pending"
    VERIFIED = "Verified"
    REJECTED = "Rejected"

    states = (
        (PENDING, "Pending"),
        (VERIFIED, "Verified"),
        (REJECTED, "Rejected"),
    )

    chain = models.ForeignKey("Chain", related_name="claims", on_delete=models.PROTECT)
    user_profile = models.ForeignKey(
        UserProfile,
        related_name="claims",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
    )

    bright_user = models.ForeignKey(
        BrightUser,
        related_name="claims",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    _status = models.CharField(max_length=10, choices=states, default=PENDING)

    passive_address = models.CharField(max_length=512, null=True, blank=True)

    amount = models.BigIntegerField()
    datetime = models.DateTimeField()
    batch = models.ForeignKey(
        "TransactionBatch",
        related_name="claims",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    def status(self):
        return self._status

    @property
    def age(self):
        return timezone.now() - self.datetime

    @property
    def tx_hash(self):
        if self.batch:
            return self.batch.tx_hash
        return None


class Chain(models.Model):
    chain_name = models.CharField(max_length=255)
    chain_id = models.CharField(max_length=255, unique=True)

    native_currency_name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    decimals = models.IntegerField(default=18)

    explorer_url = models.URLField(max_length=255, blank=True, null=True)
    rpc_url = models.URLField(max_length=255, blank=True, null=True)
    logo_url = models.URLField(max_length=255, blank=True, null=True)
    modal_url = models.URLField(max_length=255, blank=True, null=True)
    gas_image_url = models.URLField(max_length=255, blank=True, null=True)
    rpc_url_private = models.URLField(max_length=255)

    max_claim_amount = models.BigIntegerField()

    poa = models.BooleanField(default=False)

    fund_manager_address = models.CharField(max_length=255)
    wallet = models.ForeignKey(
        WalletAccount, related_name="chains", on_delete=models.PROTECT
    )

    max_gas_price = models.BigIntegerField(default=250000000000)
    gas_multiplier = models.FloatField(default=1)

    needs_funding = models.BooleanField(default=False)
    is_testnet = models.BooleanField(default=False)
    chain_type = models.CharField(
        max_length=10, choices=NetworkTypes.networks, default=NetworkTypes.EVM
    )
    order = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pk} - {self.symbol}:{self.chain_id}"

    @property
    def has_enough_funds(self):
        return self.get_manager_balance() > self.max_claim_amount * 32

    @property
    def block_scan_address(self):
        address = ""
        if self.explorer_url[-1] == "/":
            address = self.explorer_url + f"address/{self.fund_manager_address}"
        else:
            address = self.explorer_url + f"/address/{self.fund_manager_address}"
        return address

    def get_manager_balance(self):
        if not self.rpc_url_private:
            return 0

        try:
            from faucet.faucet_manager.fund_manager import EVMFundManager

            return EVMFundManager(self).w3.eth.getBalance(self.fund_manager_address)
        except:
            return 0

    def get_wallet_balance(self):
        if not self.rpc_url_private:
            return 0

        try:
            from faucet.faucet_manager.fund_manager import EVMFundManager

            return EVMFundManager(self).w3.eth.getBalance(self.wallet.address)
        except:
            return 0

    @property
    def has_enough_fees(self):
        return self.get_wallet_balance() > self.gas_price * 200000

    @property
    def gas_price(self):
        if not self.rpc_url_private:
            return self.max_gas_price + 1

        try:
            from faucet.faucet_manager.fund_manager import EVMFundManager

            return EVMFundManager(self).w3.eth.gas_price
        except:
            return self.max_gas_price + 1

    @property
    def is_gas_price_too_high(self):
        if not self.rpc_url_private:
            return True

        try:
            from faucet.faucet_manager.fund_manager import EVMFundManager

            return EVMFundManager(self).is_gas_price_too_high
        except:
            return True

    @property
    def total_claims(self):
        # return self.claims.filter(_status=ClaimReceipt.VERIFIED).count()
        return ClaimReceipt.objects.filter(
            chain=self, _status__in=[ClaimReceipt.VERIFIED, BrightUser.VERIFIED]
        ).count()

    @property
    def total_claims_since_last_monday(self):
        from faucet.faucet_manager.claim_manager import WeeklyCreditStrategy

        return self.claims.filter(
            datetime__gte=WeeklyCreditStrategy.get_last_monday(),
            _status__in=[ClaimReceipt.VERIFIED, BrightUser.VERIFIED],
        ).count()

    @property
    def total_claims_for_last_round(self):
        from faucet.faucet_manager.claim_manager import WeeklyCreditStrategy

        return self.claims.filter(
            datetime__gte=WeeklyCreditStrategy.get_second_last_monday(),
            datetime__lte=WeeklyCreditStrategy.get_last_monday(),
            _status__in=[ClaimReceipt.VERIFIED, BrightUser.VERIFIED],
        ).count()

    @property
    def total_claims_since_last_round(self):
        return self.total_claims_for_last_round + self.total_claims_since_last_monday


class GlobalSettings(models.Model):
    weekly_chain_claim_limit = models.IntegerField(default=10)


class TransactionBatch(models.Model):
    chain = models.ForeignKey(Chain, related_name="batches", on_delete=models.PROTECT)
    datetime = models.DateTimeField(auto_now_add=True)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)

    _status = models.CharField(
        max_length=10, choices=ClaimReceipt.states, default=ClaimReceipt.PENDING
    )

    updating = models.BooleanField(default=False)

    @property
    def claims_count(self):
        return self.claims.count()

    @property
    def claims_amount(self):
        return sum([c.amount for c in self.claims.all()]) / 1e18

    @property
    def age(self):
        return timezone.now() - self.datetime

    @property
    def should_be_processed(self):
        return all(
            [
                self._status == ClaimReceipt.PENDING,
                not self.tx_hash,
            ]
        )

    @property
    def status_should_be_updated(self):
        return all(
            [
                self._status == ClaimReceipt.PENDING,
                self.tx_hash is not None,
            ]
        )

    @property
    def is_expired(self):
        return self.age > timedelta(minutes=ClaimReceipt.MAX_PENDING_DURATION)
