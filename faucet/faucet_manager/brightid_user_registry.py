from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.middleware import geth_poa_middleware
from faucet.faucet_manager.brightid_user_registry_abi import bright_id_user_registry_abi
from faucet.models import Chain, BrightUser


class BrightIdUserRegistry:
    def __init__(self, chain: Chain, bright_id_user_registry_address: str):
        self.chain = chain
        self.abi = bright_id_user_registry_abi
        self.bright_id_user_registry_address = bright_id_user_registry_address

    @property
    def w3(self) -> Web3:
        assert self.chain.rpc_url_private is not None
        _w3 = Web3(Web3.HTTPProvider(self.chain.rpc_url_private))
        if self.chain.poa:
            _w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        if _w3.isConnected():
            _w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
            return _w3
        raise Exception(f"Could not connect to rpc {self.chain.rpc_url_private}")

    @property
    def contract(self):
        return self.w3.eth.contract(
            address=self.get_checksum_address(self.bright_id_user_registry_address),
            abi=self.abi,
        )

    def get_checksum_address(self, address):
        return Web3.toChecksumAddress(address.lower())

    def is_verified_user(self, address):
        return self.contract.functions.isVerifiedUser(
            self.get_checksum_address(address)
        ).call()
