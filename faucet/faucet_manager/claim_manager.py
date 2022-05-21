import abc
from abc import ABC
from brightIDfaucet import settings
from django.db import transaction
from django.utils import timezone
from faucet.faucet_manager.credit_strategy import CreditStrategy, CreditStrategyFactory
from faucet.models import ClaimReceipt, BrightUser


class ClaimManager(ABC):

    @abc.abstractmethod
    def claim(self, amount) -> ClaimReceipt:
        pass

    @abc.abstractmethod
    def get_credit_strategy(self) -> CreditStrategy:
        pass


class SimpleClaimManager(ClaimManager):

    def __init__(self, credit_strategy: CreditStrategy):
        self.credit_strategy = credit_strategy

    def claim(self, amount) -> ClaimReceipt:
        with transaction.atomic():
            bright_user = BrightUser.objects.select_for_update().get(pk=self.credit_strategy.bright_user.pk)
            self.assert_pre_claim_conditions(amount, bright_user)
            return self.credit_strategy.chain.transfer(bright_user, amount)

    def assert_pre_claim_conditions(self, amount, bright_user):
        assert amount <= self.credit_strategy.get_unclaimed()
        assert self.credit_strategy.bright_user.verification_status == BrightUser.VERIFIED

        # update receipts first
        ClaimReceipt.update_status(self.credit_strategy.chain, bright_user)

        assert not ClaimReceipt.objects.filter(
            chain=self.credit_strategy.chain,
            bright_user=bright_user,
            _status=BrightUser.PENDING
        ).exists()

    def get_credit_strategy(self) -> CreditStrategy:
        return self.credit_strategy


class MockClaimManager(SimpleClaimManager):

    def claim(self, amount) -> ClaimReceipt:
        with transaction.atomic():
            bright_user = BrightUser.objects.select_for_update().get(pk=self.credit_strategy.bright_user.pk)
            self.assert_pre_claim_conditions(amount, bright_user)

            return self.create_claim_receipt(amount, bright_user)

    def create_claim_receipt(self, amount, bright_user):
        return ClaimReceipt.objects.create(chain=self.credit_strategy.chain,
                                           bright_user=bright_user,
                                           amount=amount,
                                           datetime=timezone.now())

class ClaimManagerFactory:
    def get_default_claim_manager(self):
        return SimpleClaimManager

    def __init__(self, chain, bright_user):
        self.chain = chain
        self.bright_user = bright_user

    def get_manager(self) -> ClaimManager:
        if settings.USE_MOCK:
            _Manager = MockClaimManager
        else:
            _Manager = self.get_default_claim_manager()
        assert _Manager is not None, f"Manager for chain {self.chain.pk} not found"
        _strategy = CreditStrategyFactory(self.chain, self.bright_user).get_strategy()
        return _Manager(_strategy)
