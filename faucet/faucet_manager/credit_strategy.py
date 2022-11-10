import abc
from abc import ABC
from time import time
import datetime

from django.db.models import Sum
from django.utils import timezone

from brightIDfaucet import settings
from faucet.faucet_manager.brightid_user_registry import BrightIdUserRegistry
from faucet.models import ClaimReceipt, BrightUser, Chain


class CreditStrategy(ABC):
    def __int__(self, chain: Chain, bright_user: BrightUser):
        self.chain = chain
        self.bright_user = bright_user

    @abc.abstractmethod
    def get_claim_receipts(self):
        pass

    @abc.abstractmethod
    def get_claimed(self):
        pass

    @abc.abstractmethod
    def get_unclaimed(self):
        pass


class SimpleCreditStrategy(CreditStrategy):
    def __init__(self, chain, bright_user):
        self.chain = chain
        self.bright_user = bright_user

    def get_claim_receipts(self):
        return ClaimReceipt.objects.filter(
            chain=self.chain,
            bright_user=self.bright_user,
            _status=ClaimReceipt.VERIFIED,
        )

    def get_claimed(self):
        aggregate = self.get_claim_receipts().aggregate(Sum("amount"))
        _sum = aggregate.get("amount__sum")
        if not _sum:
            return 0
        return _sum

    def get_unclaimed(self):
        return self.chain.max_claim_amount - self.get_claimed()


class WeeklyCreditStrategy(SimpleCreditStrategy):
    def __int__(self, chain: Chain, bright_user: BrightUser):
        self.chain = chain
        self.bright_user = bright_user

    def get_claim_receipts(self):
        return ClaimReceipt.objects.filter(
            chain=self.chain,
            bright_user=self.bright_user,
            _status=ClaimReceipt.VERIFIED,
            datetime__gte=self.get_last_monday(),
        )

    @staticmethod
    def get_last_monday():
        now = int(time())
        day = 86400  # seconds in a day
        week = 7 * day
        weeks = now // week  # number of weeks since epoch
        monday = 345600  # first monday midnight
        last_monday_midnight = monday + (weeks * week)

        # last monday could be off by one week
        if last_monday_midnight > now:
            last_monday_midnight -= week

        return timezone.make_aware(
            datetime.datetime.fromtimestamp(last_monday_midnight)
        )


class ArbitrumCreditStrategy(WeeklyCreditStrategy):
    def get_unclaimed(self):
        contract_address = "0x631a12430F94207De980D9b6A744AEB4093DCeC1"
        max_claim_amount = self.chain.max_claim_amount
        is_verified_user = BrightIdUserRegistry(
            self.chain, contract_address
        ).is_verified_user(self.bright_user.address)

        if is_verified_user:
            max_claim_amount = 5000000000000000

        return max_claim_amount - self.get_claimed()


class CreditStrategyFactory:
    def __init__(self, chain, bright_user):
        self.chain = chain
        self.bright_user = bright_user

    def get_strategy_class(self):
        if self.chain.chain_id == "42161":
            return ArbitrumCreditStrategy
        return WeeklyCreditStrategy

    def get_strategy(self) -> CreditStrategy:
        _Strategy = self.get_strategy_class()
        assert _Strategy is not None, f"Strategy for chain {self.chain.pk} not found"
        return _Strategy(self.chain, self.bright_user)
