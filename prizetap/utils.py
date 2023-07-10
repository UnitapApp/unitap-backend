import random
from web3 import Web3, Account
from eth_account.messages import encode_defunct

def create_uint32_random_nonce():
    # uint32 range
    min_uint32 = 0
    max_uint32 = 2**32 - 1

    # Generate random nonce
    nonce = random.randint(min_uint32, max_uint32)
    return nonce


def raffle_hash_message(user, raffleId, nonce=None):

    abi = ["address", "uint256"]
    data = [Web3.toChecksumAddress(user), raffleId]
    if nonce:
        abi.append("uint32")
        data.append(nonce)
    message_hash = Web3().solidityKeccak(abi, data)
    hashed_message = encode_defunct(hexstr=message_hash.hex())

    return hashed_message


def sign_hashed_message(hashed_message, private_key):
    account = Account.from_key(private_key)

    signed_message = account.sign_message(hashed_message)

    return signed_message.signature.hex()