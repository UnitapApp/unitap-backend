import logging
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone
from safedelete.models import SafeDeleteModel

from authentication.models import UserProfile
from brightIDfaucet.settings import BRIGHT_ID_INTERFACE
from core.models import AbstractGlobalSettings, BigNumField, Chain, NetworkTypes
from faucet.faucet_manager.lnpay_client import LNPayClient


def get_cache_time(id):
    return int((float(int(id) % 25) / 25.0) * 180.0) + 180


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
    MAX_PENDING_DURATION = 5  # minutes
    PENDING = "Pending"
    VERIFIED = "Verified"
    REJECTED = "Rejected"
    PROCESSED_FOR_TOKENTAP = "Processed"
    PROCESSED_FOR_TOKENTAP_REJECT = "Processed_Rejected"

    states = (
        (PENDING, "Pending"),
        (VERIFIED, "Verified"),
        (REJECTED, "Rejected"),
        (PROCESSED_FOR_TOKENTAP, "Processed"),
        (PROCESSED_FOR_TOKENTAP_REJECT, "Processed_Rejected"),
    )

    faucet = models.ForeignKey(
        "Faucet", related_name="claims", on_delete=models.PROTECT
    )
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

    _status = models.CharField(max_length=30, choices=states, default=PENDING)

    to_address = models.CharField(max_length=512, null=True, blank=True)

    amount = BigNumField()
    datetime = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True)
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

    @staticmethod
    def claims_count():
        cached_count = cache.get("gastap_claims_count")
        if cached_count:
            return cached_count
        count = ClaimReceipt.objects.filter(
            _status__in=[ClaimReceipt.VERIFIED, BrightUser.VERIFIED]
        ).count()
        cache.set("gastap_claims_count", count, 600)
        return count


class Faucet(models.Model):
    chain = models.ForeignKey(Chain, related_name="faucets", on_delete=models.PROTECT)
    gas_image_url = models.URLField(max_length=255, blank=True, null=True)

    max_claim_amount = BigNumField()

    fund_manager_address = models.CharField(max_length=255)
    tokentap_contract_address = models.CharField(max_length=255, null=True, blank=True)

    needs_funding = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    is_one_time_claim = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    show_in_gastap = models.BooleanField(default=True)
    is_deprecated = models.BooleanField(default=False)

    fuel_level = models.IntegerField(default=100)

    def __str__(self):
        return (
            f"{self.chain.chain_name} - {self.pk} - "
            f"{self.chain.symbol}:{self.chain.chain_id}"
        )

    @property
    def current_fuel_level(self):
        current_fuel_level = cache.get(f"{self.pk}_current_fuel_level")
        return current_fuel_level if current_fuel_level is not None else -1

    @property
    def remaining_claim_number(self):
        remaining_claim_number = cache.get(f"{self.pk}_remaining_claim_number")
        return remaining_claim_number if remaining_claim_number is not None else -1

    @property
    def has_enough_funds(self):
        if self.get_manager_balance() > self.max_claim_amount:
            return True
        logging.warning(
            f"Faucet {self.pk}-{self.chain.chain_name} "
            "has insufficient funds in contract"
        )
        return False

    @property
    def block_scan_address(self):
        if not self.chain.explorer_url:
            return None
        if self.chain.explorer_url[-1] == "/":
            address = self.chain.explorer_url + f"address/{self.fund_manager_address}"
        else:
            address = self.chain.explorer_url + f"/address/{self.fund_manager_address}"
        return address

    @property
    def manager_balance(self):
        return self.get_manager_balance()

    def get_manager_balance(self):
        if not self.is_active or self.is_deprecated:
            return 0

        if not self.chain.rpc_url_private:
            return 0

        try:
            from faucet.faucet_manager.fund_manager import (
                EVMFundManager,
                SolanaFundManager,
            )

            if (
                self.chain.chain_type == NetworkTypes.EVM
                or int(self.chain.chain_id) == 500
            ):
                # if self.chain_id == 500:
                #     logging.debug("chain XDC NONEVM is checking its balances")
                funds = EVMFundManager(self).get_balance(self.fund_manager_address)
                return funds

            elif self.chain.chain_type == NetworkTypes.SOLANA:
                fund_manager = SolanaFundManager(self)
                v = fund_manager.w3.get_balance(fund_manager.lock_account_address).value
                return v
            elif self.chain.chain_type == NetworkTypes.LIGHTNING:
                lnpay_client = LNPayClient(
                    self.chain.rpc_url_private,
                    self.chain.wallet.main_key,
                    self.fund_manager_address,
                )
                return lnpay_client.get_balance()

            raise Exception("Invalid chain type")
        except Exception as e:
            logging.exception(
                f"Error getting manager balance for "
                f"{self.chain.chain_name} error is {e}"
            )
            return 0

    @property
    def is_gas_price_too_high(self):
        if not self.is_active or self.is_deprecated:
            return True

        if not self.chain.rpc_url_private:
            return True

        try:
            from faucet.faucet_manager.fund_manager import EVMFundManager

            return EVMFundManager(self).is_gas_price_too_high
        except Exception:  # noqa: E722
            logging.exception(f"Error getting gas price for {self.chain.chain_name}")
            return True

    @property
    def total_claims(self):
        cached_total_claims = cache.get(f"gas_tap_chain_total_claims_{self.pk}")
        if cached_total_claims:
            return cached_total_claims
        total_claims = ClaimReceipt.objects.filter(
            faucet=self, _status__in=[ClaimReceipt.VERIFIED, BrightUser.VERIFIED]
        ).count()
        cache.set(
            f"gas_tap_chain_total_claims_{self.pk}",
            total_claims,
            get_cache_time(self.pk),
        )
        return total_claims

    @property
    def total_claims_this_round(self):
        cached_total_claims_this_round = cache.get(
            f"gas_tap_chain_total_claims_this_round_{self.pk}"
        )
        if cached_total_claims_this_round:
            return cached_total_claims_this_round
        from faucet.faucet_manager.claim_manager import RoundCreditStrategy

        total_claims_this_round = ClaimReceipt.objects.filter(
            faucet=self,
            datetime__gte=RoundCreditStrategy.get_start_of_the_round(),
            _status__in=[ClaimReceipt.VERIFIED],
        ).count()
        cache.set(
            f"gas_tap_chain_total_claims_this_round_{self.pk}",
            total_claims_this_round,
            get_cache_time(self.pk),
        )
        return total_claims_this_round

    @property
    def total_claims_since_last_round(self):
        cached_total_claims_since_last_round = cache.get(
            f"gas_tap_chain_total_claims_since_last_round_{self.pk}"
        )
        if cached_total_claims_since_last_round:
            return cached_total_claims_since_last_round
        from faucet.faucet_manager.claim_manager import RoundCreditStrategy

        total_claims_since_last_round = ClaimReceipt.objects.filter(
            faucet=self,
            datetime__gte=RoundCreditStrategy.get_start_of_previous_round(),
            _status__in=[ClaimReceipt.VERIFIED],
        ).count()
        cache.set(
            f"gas_tap_chain_total_claims_since_last_round_{self.pk}",
            total_claims_since_last_round,
            get_cache_time(self.pk),
        )
        return total_claims_since_last_round


class GlobalSettings(AbstractGlobalSettings):
    pass


class TransactionBatch(models.Model):
    faucet = models.ForeignKey(
        Faucet, related_name="batches", on_delete=models.PROTECT, db_index=True
    )
    datetime = models.DateTimeField(auto_now_add=True)
    tx_hash = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    _status = models.CharField(
        max_length=30,
        choices=ClaimReceipt.states,
        default=ClaimReceipt.PENDING,
        db_index=True,
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


class LightningConfig(models.Model):
    period = models.IntegerField(default=64800)
    period_max_cap = models.BigIntegerField()
    claimed_amount = models.BigIntegerField(default=0)
    current_round = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class DonationReceipt(models.Model):
    states = (
        (ClaimReceipt.PENDING, "Pending"),
        (ClaimReceipt.VERIFIED, "Verified"),
        (ClaimReceipt.REJECTED, "Rejected"),
    )
    user_profile = models.ForeignKey(
        UserProfile,
        related_name="donations",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )
    tx_hash = models.CharField(max_length=255, blank=False, null=False)
    faucet = models.ForeignKey(
        Faucet,
        related_name="donation",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )
    value = models.CharField(max_length=255, null=True, blank=True)
    total_price = models.CharField(max_length=255, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=30,
        choices=states,
        default=ClaimReceipt.PENDING,
    )

    class Meta:
        unique_together = ("faucet", "tx_hash")


class DonationContract(SafeDeleteModel):
    contract_address = models.CharField(max_length=255, blank=False, null=False)
    faucet = models.ForeignKey(
        Faucet,
        related_name="donation_contracts",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                "faucet",
                name="unique_active_donation_contract",
                condition=Q(deleted__isnull=True),
            ),
            UniqueConstraint(
                Lower("contract_address"),
                "faucet",
                name="unique_donation_contract_address",
            ),
        ]
