from django.core.exceptions import BadRequest
from solders.pubkey import Pubkey

from core.utils import Web3Utils

from .models import Chain, NetworkTypes


def address_validator(address, chain: Chain):
    is_address_valid = False
    if chain.chain_type == NetworkTypes.LIGHTNING:
        return
    elif chain.chain_type == NetworkTypes.EVM:
        try:
            Web3Utils.to_checksum_address(address)
            return
        except ValueError:
            is_address_valid = False
    elif chain.chain_type == NetworkTypes.SOLANA:
        try:
            pub_key = Pubkey.from_string(address)
            is_address_valid = pub_key.is_on_curve()
        except ValueError:
            is_address_valid = False

    if not is_address_valid:
        raise BadRequest(f"Address: {address} is not valid")
