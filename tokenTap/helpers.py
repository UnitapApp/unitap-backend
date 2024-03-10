import random

from core.models import NetworkTypes, WalletAccount
from core.utils import TimeUtils, Web3Utils

from .models import GlobalSettings, TokenDistributionClaim


def create_uint32_random_nonce():
    # uint32 range
    min_uint32 = 0
    max_uint32 = 2**32 - 1

    # Generate random nonce
    nonce = random.randint(min_uint32, max_uint32)
    return nonce


def hash_message(address, token, amount, nonce):
    hashed_message = Web3Utils.hash_message(
        ["address", "address", "uint256", "uint32"],
        [
            Web3Utils.to_checksum_address(address),
            Web3Utils.to_checksum_address(token),
            int(amount),
            nonce,
        ],
    )
    return hashed_message


def sign_hashed_message(hashed_message):
    private_key = WalletAccount.objects.get(network_type=NetworkTypes.EVM).private_key
    return Web3Utils.sign_hashed_message(private_key, hashed_message)


class ClaimStrategy:
    MONTHLY = "monthly"
    WEEKLY = "weekly"

    def __init__(self, strategy, period=None) -> None:
        self.strategy = strategy
        self.period = period

    def get_start_of_the_round(self):
        if self.strategy == self.MONTHLY:
            return TimeUtils.get_first_day_of_the_month()
        elif self.strategy == self.WEEKLY:
            return TimeUtils.get_first_day_of_the_week()
        else:
            # TODO: fixme - period in seconds
            pass

    def get_start_of_previous_round(self):
        if self.strategy == self.MONTHLY:
            return TimeUtils.get_first_day_of_last_month()
        elif self.strategy == self.WEEKLY:
            return TimeUtils.get_first_day_of_last_week()
        else:
            # TODO: fixme - period in seconds
            pass


def has_credit_left(distribution, user_profile):
    strategy = ClaimStrategy(
        GlobalSettings.get("tokentap_round_claim_strategy", ClaimStrategy.WEEKLY)
    )
    distribution_claims = TokenDistributionClaim.objects.filter(
        user_profile=user_profile,
        token_distribution=distribution,
        created_at__gte=strategy.get_start_of_the_round(),
    ).count()

    if distribution_claims > 0:
        return False

    return TokenDistributionClaim.objects.filter(
        user_profile=user_profile,
        created_at__gte=strategy.get_start_of_the_round(),
    ).count() < int(GlobalSettings.get("tokentap_round_claim_limit", "3"))
