import abc
from abc import ABC

from django.utils import timezone

from faucet.faucet_manager.credit_strategy import CreditStrategy, CreditStrategyFactory
from faucet.models import ClaimReceipt, BrightUser


class ClaimManager(ABC):

    @abc.abstractmethod
    def claim(self, amount):
        pass


class SimpleClaimManager(ClaimManager):

    def __init__(self, credit_strategy: CreditStrategy):
        self.credit_strategy = credit_strategy

    def claim(self, amount):
        assert amount <= self.credit_strategy.get_unclaimed()
        assert self.credit_strategy.bright_user.verification_status == BrightUser.VERIFIED

        ClaimReceipt.objects.create(chain=self.credit_strategy.chain,
                                    bright_user=self.credit_strategy.bright_user,
                                    amount=amount,
                                    datetime=timezone.now())


class ClaimManagerFactory:

    default_claim_manager = {
        '100': SimpleClaimManager,
        '74': SimpleClaimManager
    }

    def __init__(self, chain, bright_user):
        self.chain = chain
        self.bright_user = bright_user

    def get_manager(self) -> ClaimManager:
        _Manager = self.default_claim_manager[self.chain.chain_id]
        assert _Manager is not None, f"Manager for chain {self.chain.pk} not found"
        _strategy = CreditStrategyFactory(self.chain, self.bright_user).get_strategy()
        return _Manager(_strategy)
