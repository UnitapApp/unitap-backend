import abc
from abc import ABC

from faucet.faucet_manager.credit_strategy import CreditStrategy


class ClaimManager(ABC):

    @abc.abstractmethod
    def claim(self, amount):
        pass


class SimpleClaimManager(ClaimManager):

    def __init__(self, credit_strategy: CreditStrategy):
        self.credit_strategy = credit_strategy

    def claim(self, amount):
        assert amount <= self.credit_strategy.get_unclaimed()


class ClaimManagerFactory:

    def __init__(self):
        pass

    def get_manager(self) -> ClaimManager:
        pass
