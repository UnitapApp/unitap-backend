from django.utils import timezone
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.middleware import geth_poa_middleware
from faucet.faucet_manager.fund_manager_abi import manager_abi
from faucet.models import Chain, BrightUser, ClaimReceipt


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

    @property
    def contract(self):
        return self.w3.eth.contract(address=self.chain.fund_manager_address, abi=self.abi)

    def transfer(self, bright_user: BrightUser, pending_receipt: ClaimReceipt, amount: int) -> ClaimReceipt:
        tx = self.single_eth_transfer_signed_tx(amount, bright_user.address)
        pending_receipt.tx_hash = tx['hash'].hex()
        pending_receipt.save()
        self.w3.eth.send_raw_transaction(tx.rawTransaction)
        return pending_receipt

    def single_eth_transfer_signed_tx(self, amount: int, to: str):
        nonce = self.w3.eth.get_transaction_count(self.account.address, "pending")
        tx_function = self.contract.functions.withdrawEth(amount, to)
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
        except TimeExhausted:
            return False

    def update_receipt_status(self, claim_receipt: ClaimReceipt):
        if not claim_receipt.tx_hash:
            return

        if self.is_tx_verified(claim_receipt.tx_hash):
            claim_receipt._status = ClaimReceipt.VERIFIED
        elif claim_receipt.is_expired():
            claim_receipt._status = ClaimReceipt.REJECTED
        claim_receipt.save()

