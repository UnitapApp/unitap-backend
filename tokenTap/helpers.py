import random

from core.models import NetworkTypes, WalletAccount
from core.utils import Web3Utils
from faucet.faucet_manager.credit_strategy import RoundCreditStrategy
from faucet.models import GlobalSettings

from .models import TokenDistributionClaim


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


def has_credit_left(user_profile):
    return (
        TokenDistributionClaim.objects.filter(
            user_profile=user_profile,
            created_at__gte=RoundCreditStrategy.get_start_of_the_round(),
        ).count()
        < GlobalSettings.objects.first().tokentap_round_claim_limit
    )
