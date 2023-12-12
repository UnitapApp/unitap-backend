import abc
import datetime
from abc import ABC
from time import time

import pytz
from django.db.models import Sum
from django.utils import timezone

from authentication.models import UserProfile
from faucet.models import Chain, ClaimReceipt


class CreditStrategy(ABC):
    def __int__(self, chain: Chain, user_profile: UserProfile):
        self.chain = chain
        self.user_profile = user_profile

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
    def __init__(self, chain, user_profile):
        self.chain = chain
        self.user_profile = user_profile

    def get_claim_receipts(self):
        return ClaimReceipt.objects.filter(
            chain=self.chain,
            user_profile=self.user_profile,
            _status=ClaimReceipt.VERIFIED,
        )

    def get_claimed(self):
        aggregate = self.get_claim_receipts().aggregate(Sum("amount"))
        _sum = aggregate.get("amount__sum")
        if not _sum:
            return 0
        return _sum

    def get_unclaimed(self):
        return int(self.chain.max_claim_amount) - int(self.get_claimed())


class RoundCreditStrategy(SimpleCreditStrategy):
    def __int__(self, chain: Chain, user_profile: UserProfile):
        self.chain = chain
        self.user_profile = user_profile

    def get_claim_receipts(self):
        return ClaimReceipt.objects.filter(
            chain=self.chain,
            user_profile=self.user_profile,
            _status=ClaimReceipt.VERIFIED,
            datetime__gte=self._get_first_day_of_the_month(),
        )

    @staticmethod
    def get_start_of_the_round():
        return RoundCreditStrategy._get_first_day_of_the_week()
        return RoundCreditStrategy._get_first_day_of_the_month()

    @staticmethod
    def get_start_of_previous_round():
        return RoundCreditStrategy._get_first_day_of_last_week()
        return RoundCreditStrategy._get_first_day_of_last_month()

    @classmethod
    def _get_first_day_of_the_month(cls):
        now = datetime.datetime.now(pytz.timezone("UTC"))
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return first_day

    @classmethod
    def _get_first_day_of_last_month(cls):
        now = datetime.datetime.now(pytz.timezone("UTC"))
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = first_day - datetime.timedelta(days=1)
        first_day_of_last_month = last_month.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        return first_day_of_last_month

    @classmethod
    def _get_first_day_of_the_week(cls):
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

    @classmethod
    def _get_first_day_of_last_week(cls):
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
            datetime.datetime.fromtimestamp(last_monday_midnight - week)
        )


class OneTimeCreditStrategy(SimpleCreditStrategy):
    def __int__(self, chain: Chain, user_profile: UserProfile):
        self.chain = chain
        self.user_profile = user_profile

    def get_claim_receipts(self):
        return ClaimReceipt.objects.filter(
            chain=self.chain,
            user_profile=self.user_profile,
            _status=ClaimReceipt.VERIFIED,
            # 1 December 2023
            datetime__gte=datetime.datetime(
                2023, 12, 1, 0, 0, 0, 0, pytz.timezone("UTC")
            ),  # also change in views.py
        )


class CreditStrategyFactory:
    def __init__(self, chain: Chain, user_profile):
        self.chain = chain
        self.user_profile = user_profile

    def get_strategy_class(self):
        if self.chain.is_one_time_claim:
            return OneTimeCreditStrategy
        return RoundCreditStrategy

    def get_strategy(self) -> CreditStrategy:
        _Strategy = self.get_strategy_class()
        assert _Strategy is not None, f"Strategy for chain {self.chain.pk} not found"
        return _Strategy(self.chain, self.user_profile)
