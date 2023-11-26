import abc
import datetime
from abc import ABC

import pytz
from django.db.models import Sum

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


# class WeeklyCreditStrategy(SimpleCreditStrategy):
#     def __int__(self, chain: Chain, user_profile: UserProfile):
#         self.chain = chain
#         self.user_profile = user_profile

#     def get_claim_receipts(self):
#         return ClaimReceipt.objects.filter(
#             chain=self.chain,
#             user_profile=self.user_profile,
#             _status=ClaimReceipt.VERIFIED,
#             datetime__gte=self.get_last_monday(),
#         )

#     @staticmethod
#     def get_last_monday():
#         now = int(time())
#         day = 86400  # seconds in a day
#         week = 7 * day
#         weeks = now // week  # number of weeks since epoch
#         monday = 345600  # first monday midnight
#         last_monday_midnight = monday + (weeks * week)

#         # last monday could be off by one week
#         if last_monday_midnight > now:
#             last_monday_midnight -= week

#         return timezone.make_aware(datetime.datetime.fromtimestamp(last_monday_midnight))

#     @staticmethod
#     def get_second_last_monday():
#         now = int(time())
#         day = 86400  # seconds in a day
#         week = 7 * day
#         weeks = now // week  # number of weeks since epoch
#         monday = 345600  # first monday midnight
#         last_monday_midnight = monday + (weeks * week)

#         # last monday could be off by one week
#         if last_monday_midnight > now:
#             last_monday_midnight -= week

#         return timezone.make_aware(datetime.datetime.fromtimestamp(last_monday_midnight - week))


# class ArbitrumCreditStrategy(WeeklyCreditStrategy):
#     def get_unclaimed(self):
#         contract_address = "0x631a12430F94207De980D9b6A744AEB4093DCeC1"
#         max_claim_amount = self.chain.max_claim_amount
#         is_verified_user = BrightIdUserRegistry(self.chain, contract_address).is_verified_user(
#             self.user_profile.initial_context_id
#         )

#         if is_verified_user:
#             max_claim_amount = 5000000000000000

#         return max_claim_amount - self.get_claimed()


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
        return RoundCreditStrategy._get_first_day_of_the_month()

    @staticmethod
    def get_start_of_previous_round():
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
        first_day_of_last_month = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return first_day_of_last_month


class OneTimeCreditStrategy(SimpleCreditStrategy):
    def __int__(self, chain: Chain, user_profile: UserProfile):
        self.chain = chain
        self.user_profile = user_profile

    def get_claim_receipts(self):
        return ClaimReceipt.objects.filter(
            chain=self.chain,
            user_profile=self.user_profile,
            _status=ClaimReceipt.VERIFIED,
            # 1 November 2023
            datetime__gte=datetime.datetime(2023, 11, 1, 0, 0, 0, 0, pytz.timezone("UTC")),
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
