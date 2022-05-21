import abc
from abc import ABC

from django.db.models import Sum
from brightIDfaucet import settings
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
        return ClaimReceipt.objects.filter(chain=self.chain, bright_user=self.bright_user)

    def get_claimed(self):
        aggregate = self.get_claim_receipts().aggregate(Sum("amount"))
        _sum = aggregate.get('amount__sum')
        if not _sum:
            return 0
        return _sum

    def get_unclaimed(self):
        return self.chain.max_claim_amount - self.get_claimed()


class CreditStrategyFactory:

    def get_default_credit_strategy(self):
        return SimpleCreditStrategy

    def __init__(self, chain, bright_user):
        self.chain = chain
        self.bright_user = bright_user

    def get_strategy(self) -> CreditStrategy:
        if settings.USE_MOCK:
            _Strategy = SimpleCreditStrategy
        else:
            _Strategy = self.get_default_credit_strategy()
        assert _Strategy is not None, f"Strategy for chain {self.chain.pk} not found"
        return _Strategy(self.chain, self.bright_user)