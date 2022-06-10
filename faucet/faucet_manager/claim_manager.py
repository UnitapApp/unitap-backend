import abc
from abc import ABC

from celery.result import AsyncResult
from django.utils import timezone

from faucet.faucet_manager.credit_strategy import CreditStrategy, CreditStrategyFactory
from faucet.faucet_manager.fund_manager import EVMFundManager
from faucet.models import ClaimReceipt, BrightUser
from django.db import transaction

from faucet.tasks import broadcast_and_wait_for_receipt


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

    @property
    def fund_manager(self):
        return EVMFundManager(self.credit_strategy.chain)

    def claim(self, amount):
        self.update_pending_receipts_status()
        with transaction.atomic():
            bright_user = BrightUser.objects.select_for_update().get(pk=self.credit_strategy.bright_user.pk)
            self.assert_pre_claim_conditions(amount, bright_user)
            pending_receipt = self.create_pending_claim_receipt(amount)
            broadcast_and_wait_for_receipt.delay(chain_id=self.credit_strategy.chain.pk,
                                                 bright_user_id=bright_user.pk,
                                                 pending_receipt_id=pending_receipt.pk,
                                                 amount=amount)

    def update_pending_receipts_status(self):
        for receipt in ClaimReceipt.objects.filter(
                chain=self.credit_strategy.chain,
                bright_user=self.credit_strategy.bright_user,
                _status=BrightUser.PENDING):
            self.fund_manager.update_receipt_status(receipt)

    def create_pending_claim_receipt(self, amount):
        return ClaimReceipt.objects.create(chain=self.credit_strategy.chain,
                                           bright_user=self.credit_strategy.bright_user,
                                           datetime=timezone.now(),
                                           amount=amount,
                                           _status=ClaimReceipt.PENDING)

    def assert_pre_claim_conditions(self, amount, bright_user):
        assert amount <= self.credit_strategy.get_unclaimed()
        assert self.credit_strategy.bright_user.verification_status == BrightUser.VERIFIED
        assert not ClaimReceipt.objects.filter(
            chain=self.credit_strategy.chain,
            bright_user=bright_user,
            _status=BrightUser.PENDING
        ).exists()

    def get_credit_strategy(self) -> CreditStrategy:
        return self.credit_strategy


class ClaimManagerFactory:

    def __init__(self, chain, bright_user):
        self.chain = chain
        self.bright_user = bright_user

    def get_manager_class(self):
        return SimpleClaimManager

    def get_manager(self) -> ClaimManager:
        _Manager = self.get_manager_class()
        assert _Manager is not None, f"Manager for chain {self.chain.pk} not found"
        _strategy = CreditStrategyFactory(self.chain, self.bright_user).get_strategy()
        return _Manager(_strategy)
