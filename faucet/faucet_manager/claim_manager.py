import abc
from abc import ABC

import rest_framework.exceptions
from django.db import transaction
from django.utils import timezone

from authentication.models import UserProfile
from faucet.faucet_manager.credit_strategy import (
    CreditStrategy,
    CreditStrategyFactory,
    RoundCreditStrategy,
)
from faucet.faucet_manager.fund_manager import EVMFundManager
from faucet.models import BrightUser, ClaimReceipt, GlobalSettings


class ClaimManager(ABC):
    @abc.abstractmethod
    def claim(self, amount, to_address=None, ups=[]) -> ClaimReceipt:
        pass

    @abc.abstractmethod
    def get_credit_strategy(self) -> CreditStrategy:
        pass


class SimpleClaimManager(ClaimManager):
    def __init__(self, credit_strategy: CreditStrategy):
        self.credit_strategy = credit_strategy

    @property
    def fund_manager(self):
        return EVMFundManager(self.credit_strategy.faucet)

    def claim(self, amount, to_address=None, ups=[]):
        with transaction.atomic():
            user_profile = UserProfile.objects.select_for_update().get(
                pk=self.credit_strategy.user_profile.pk
            )
            self.assert_pre_claim_conditions(amount, user_profile, ups)
            return self.create_pending_claim_receipt(
                amount, to_address, ups
            )  # all pending claims will be processed periodically

    def assert_pre_claim_conditions(self, amount, user_profile, ups=[]):
        assert amount <= self.credit_strategy.get_unclaimed()
        # assert self.user_is_meet_verified() is True
        for up in ups:
            assert up not in self.credit_strategy.faucet.used_unitap_pass_list
        assert not ClaimReceipt.objects.filter(
            faucet__chain=self.credit_strategy.faucet.chain,
            user_profile=user_profile,
            _status=ClaimReceipt.PENDING,
        ).exists()

    def create_pending_claim_receipt(self, amount, to_address, ups=[]):
        if to_address is None:
            raise rest_framework.exceptions.ParseError("wallet address is required")
        _faucet = self.credit_strategy.faucet
        _user_profile = self.credit_strategy.user_profile

        for up in ups:
            _faucet.used_unitap_pass_list.append(up)

        return ClaimReceipt.objects.create(
            faucet=_faucet,
            user_profile=_user_profile,
            datetime=timezone.now(),
            amount=amount,
            _status=ClaimReceipt.PENDING,
            to_address=to_address,
        )

    def get_credit_strategy(self) -> CreditStrategy:
        return self.credit_strategy

    def user_is_meet_verified(self) -> bool:
        return self.credit_strategy.user_profile.is_meet_verified


class LimitedChainClaimManager(SimpleClaimManager):
    def get_round_limit(self):
        limit = int(GlobalSettings.get("gastap_round_claim_limit", "5"))
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

    def assert_pre_claim_conditions(self, amount, user_profile, ups):
        super().assert_pre_claim_conditions(amount, user_profile, ups)
        total_claims = self.get_total_round_claims(user_profile)
        assert total_claims < self.get_round_limit()


class ClaimManagerFactory:
    def __init__(self, faucet, user_profile):
        self.faucet = faucet
        self.user_profile = user_profile

    def get_manager_class(self):
        return LimitedChainClaimManager

    def get_manager(self) -> ClaimManager:
        _Manager = self.get_manager_class()
        assert _Manager is not None, f"Manager for chain {self.faucet.pk} not found"
        _strategy = CreditStrategyFactory(self.faucet, self.user_profile).get_strategy()
        return _Manager(_strategy)
