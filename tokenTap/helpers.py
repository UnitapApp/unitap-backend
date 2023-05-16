import random
from web3 import Web3, Account
from eth_abi import encode_abi, encode_single

from authentication.models import NetworkTypes
from faucet.models import WalletAccount


def create_uint32_random_nonce():
    # uint32 range
    min_uint32 = 0
    max_uint32 = 2**32 - 1

    # Generate random nonce
    nonce = random.randint(min_uint32, max_uint32)
    return nonce


def hash_message(user, token, amount, nonce):
    # Convert addresses from hex to bytes
    # user_bytes = Web3.toBytes(hexstr=user)
    # user_bytes = encode_single("address", user)
    # print("user_bytes", user_bytes)
    # # token_bytes = Web3.toBytes(hexstr=token)
    # token_bytes = encode_single("address", token)

    # amount_ = encode_single("uint256", amount)
    # nonce_ = encode_single("uint32", nonce)

    # Pack the values
    packed_message = encode_abi(
        ["address", "address", "uint256", "uint32"],
        [user, token, amount, nonce],
    )

    # Hash the data
    hashed_message = Web3.keccak(text=str(packed_message))

    return hashed_message


def sign_hashed_message(hashed_message):

    private_key = WalletAccount.objects.get(network_type=NetworkTypes.EVM).private_key

    # Sign the message
    signed_message = Account.signHash(hashed_message, private_key)

    return signed_message
