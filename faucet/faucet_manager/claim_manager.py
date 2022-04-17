import abc
from abc import ABC

from django.db import transaction
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
        with transaction.atomic():
            bright_user = BrightUser.objects.select_for_update().get(pk=self.credit_strategy.bright_user.pk)

            self.assert_pre_claim_conditions(amount, bright_user)
            self.create_claim_receipt(amount, bright_user)

    def create_claim_receipt(self, amount, bright_user):
        ClaimReceipt.objects.create(chain=self.credit_strategy.chain,
                                    bright_user=bright_user,
                                    amount=amount,
                                    datetime=timezone.now())

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
