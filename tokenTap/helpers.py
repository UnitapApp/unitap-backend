import random
from web3 import Web3, Account
from eth_abi import encode_abi
from faucet.faucet_manager.credit_strategy import WeeklyCreditStrategy
from faucet.models import Chain, GlobalSettings
from .models import TokenDistributionClaim
from authentication.models import NetworkTypes
from faucet.models import WalletAccount
from eth_account.messages import encode_defunct


def create_uint32_random_nonce():
    # uint32 range
    min_uint32 = 0
    max_uint32 = 2**32 - 1

    # Generate random nonce
    nonce = random.randint(min_uint32, max_uint32)
    return nonce


def hash_message(user, token, amount, nonce):

    message_hash = Web3().solidityKeccak(
        ["address", "address", "uint256", "uint32"],
        [Web3.toChecksumAddress(user), Web3.toChecksumAddress(token), amount, nonce],
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
            created_at__gte=WeeklyCreditStrategy.get_last_monday(),
        ).count()
        < GlobalSettings.objects.first().tokentap_weekly_claim_limit
    )
