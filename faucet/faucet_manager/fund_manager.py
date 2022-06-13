from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.middleware import geth_poa_middleware
from faucet.faucet_manager.fund_manager_abi import manager_abi
from faucet.models import Chain, BrightUser


class EVMFundManager:

    def __init__(self, chain: Chain):
        self.chain = chain
        self.abi = manager_abi

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
    def account(self) -> LocalAccount:
        return self.w3.eth.account.privateKeyToAccount(self.chain.wallet.main_key)

    def get_checksum_address(self):
        return Web3.toChecksumAddress(self.chain.fund_manager_address.lower())

    @property
    def contract(self):
        return self.w3.eth.contract(address=self.get_checksum_address(), abi=self.abi)

    def transfer(self, bright_user: BrightUser, amount: int):
        tx = self.single_eth_transfer_signed_tx(amount, bright_user.address)
        self.w3.eth.send_raw_transaction(tx.rawTransaction)
        return tx['hash'].hex()

    def multi_transfer(self, data):
        tx = self.multi_eth_transfer_signed_tx(data)
        self.w3.eth.send_raw_transaction(tx.rawTransaction)
        return tx['hash'].hex()

    def single_eth_transfer_signed_tx(self, amount: int, to: str):
        tx_function = self.contract.functions.withdrawEth(amount, to)
        return self.prepare_tx_for_broadcast(tx_function)

    def multi_eth_transfer_signed_tx(self, data):
        tx_function = self.contract.functions.multiWithdrawEth(data)
        return self.prepare_tx_for_broadcast(tx_function)

    def prepare_tx_for_broadcast(self, tx_function):
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_estimation = tx_function.estimateGas({'from': self.account.address})
        tx_data = tx_function.buildTransaction({
            'nonce': nonce,
            'from': self.account.address,
            'gas': gas_estimation,
            'gasPrice': self.w3.eth.gas_price
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.account.key)
        return signed_tx

    def is_tx_verified(self, tx_hash):
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt['status'] == 1:
                return True
            return False
        except TimeExhausted:
            raise
