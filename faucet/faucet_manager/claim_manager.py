import abc
import logging
from abc import ABC

from django.db import transaction
from django.utils import timezone

from authentication.models import UserProfile
from core.models import NetworkTypes
from faucet.faucet_manager.credit_strategy import (
    CreditStrategy,
    CreditStrategyFactory,
    RoundCreditStrategy,
)
from faucet.faucet_manager.fund_manager import EVMFundManager
from faucet.faucet_manager.lnpay_client import LNPayClient
from faucet.models import BrightUser, ClaimReceipt, GlobalSettings


class ClaimManager(ABC):
    @abc.abstractmethod
    def claim(self, amount, passive_address=None) -> ClaimReceipt:
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

    def claim(self, amount, passive_address=None):
        with transaction.atomic():
            user_profile = UserProfile.objects.select_for_update().get(
                pk=self.credit_strategy.user_profile.pk
            )
            self.assert_pre_claim_conditions(amount, user_profile)
            return self.create_pending_claim_receipt(
                amount, passive_address
            )  # all pending claims will be processed periodically

    def assert_pre_claim_conditions(self, amount, user_profile):
        assert amount <= self.credit_strategy.get_unclaimed()
        assert self.user_is_meet_verified() is True
        assert not ClaimReceipt.objects.filter(
            chain=self.credit_strategy.chain,
            user_profile=user_profile,
            _status=ClaimReceipt.PENDING,
        ).exists()

    def create_pending_claim_receipt(self, amount, passive_address):
        return ClaimReceipt.objects.create(
            chain=self.credit_strategy.chain,
            user_profile=self.credit_strategy.user_profile,
            datetime=timezone.now(),
            amount=amount,
            _status=ClaimReceipt.PENDING,
            passive_address=passive_address,
        )

    def get_credit_strategy(self) -> CreditStrategy:
        return self.credit_strategy

    def user_is_meet_verified(self) -> bool:
        return self.credit_strategy.user_profile.is_meet_verified


class LimitedChainClaimManager(SimpleClaimManager):
    def get_round_limit(self):
        limit = GlobalSettings.objects.first().gastap_round_claim_limit
        return limit

    @staticmethod
    def get_total_round_claims(user_profile):
        start_of_the_round = RoundCreditStrategy.get_start_of_the_round()
        return ClaimReceipt.objects.filter(
            user_profile=user_profile,
            _status__in=[
                ClaimReceipt.PENDING,
                ClaimReceipt.VERIFIED,
                BrightUser.PENDING,
                BrightUser.VERIFIED,
            ],
            datetime__gte=start_of_the_round,
        ).count()

    def assert_pre_claim_conditions(self, amount, user_profile):
        super().assert_pre_claim_conditions(amount, user_profile)
        total_claims = self.get_total_round_claims(user_profile)
        assert total_claims < self.get_round_limit()


class LightningClaimManger(LimitedChainClaimManager):
    def claim(self, amount, passive_address):
        try:
            lnpay_client = LNPayClient(
                self.credit_strategy.chain.rpc_url_private,
                self.credit_strategy.chain.wallet.main_key,
                self.credit_strategy.chain.fund_manager_address,
            )
            decoded_invoice = lnpay_client.decode_invoice(passive_address)
        except Exception as e:
            logging.error(e)
            raise AssertionError("Could not decode the invoice")
        assert int(decoded_invoice["num_satoshis"]) == amount, "Invalid amount"
        return super().claim(amount, passive_address)


class ClaimManagerFactory:
    def __init__(self, chain, user_profile):
        self.chain = chain
        self.user_profile = user_profile

    def get_manager_class(self):
        if self.chain.chain_type == NetworkTypes.LIGHTNING:
            return LightningClaimManger
        return LimitedChainClaimManager

    def get_manager(self) -> ClaimManager:
        _Manager = self.get_manager_class()
        assert _Manager is not None, f"Manager for chain {self.chain.pk} not found"
        _strategy = CreditStrategyFactory(self.chain, self.user_profile).get_strategy()
        return _Manager(_strategy)
