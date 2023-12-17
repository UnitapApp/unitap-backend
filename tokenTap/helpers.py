import random

from eth_account.messages import encode_defunct
from web3 import Account, Web3

from core.models import NetworkTypes, WalletAccount
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


def hash_message(user, token, amount, nonce):
    message_hash = Web3().solidity_keccak(
        ["address", "address", "uint256", "uint32"],
        [
            Web3.to_checksum_address(user),
            Web3.to_checksum_address(token),
            amount,
            nonce,
        ],
    )
    hashed_message = encode_defunct(hexstr=message_hash.hex())

    return hashed_message


def sign_hashed_message(hashed_message):
    private_key = WalletAccount.objects.get(network_type=NetworkTypes.EVM).private_key
    account = Account.from_key(private_key)

    signed_message = account.sign_message(hashed_message)

    return signed_message.signature.hex()


def has_weekly_credit_left(user_profile):
    return (
        TokenDistributionClaim.objects.filter(
            user_profile=user_profile,
            created_at__gte=RoundCreditStrategy.get_start_of_the_round(),
        ).count()
        < GlobalSettings.objects.first().tokentap_round_claim_limit
    )
