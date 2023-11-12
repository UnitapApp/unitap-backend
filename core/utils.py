import datetime

import pytz
from web3 import Web3
from web3.contract.contract import Contract, ContractFunction
from web3.middleware import geth_poa_middleware
from web3.types import TxParams, Type


class TimeUtils:
    #     @staticmethod
    #     def get_last_monday():
    #         now = int(time())
    #         day = 86400  # seconds in a day
    #         week = 7 * day
    #         weeks = now // week  # number of weeks since epoch
    #         monday = 345600  # first monday midnight
    #         last_monday_midnight = monday + (weeks * week)

    #         # last monday could be off by one week
    #         if last_monday_midnight > now:
    #             last_monday_midnight -= week

    #         return timezone.make_aware(
    #             datetime.datetime.fromtimestamp(last_monday_midnight)
    #         )

    #     @staticmethod
    #     def get_second_last_monday():
    #         now = int(time())
    #         day = 86400  # seconds in a day
    #         week = 7 * day
    #         weeks = now // week  # number of weeks since epoch
    #         monday = 345600  # first monday midnight
    #         last_monday_midnight = monday + (weeks * week)

    #         # last monday could be off by one week
    #         if last_monday_midnight > now:
    #             last_monday_midnight -= week

    #         return timezone.make_aware(
    #             datetime.datetime.fromtimestamp(last_monday_midnight - week)
    #         )

    @staticmethod
    def get_first_day_of_the_month():
        now = datetime.datetime.now(pytz.timezone("UTC"))
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return first_day

    @staticmethod
    def get_first_day_of_last_month():
        now = datetime.datetime.now(pytz.timezone("UTC"))
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = first_day - datetime.timedelta(days=1)
        first_day_of_last_month = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return first_day_of_last_month


class Web3Utils:
    def __init__(self, rpc_url, poa=False) -> None:
        self._rpc_url = rpc_url
        self._w3 = None
        self._account = None
        self._contract = None
        self._poa = poa

    @property
    def w3(self) -> Web3:
        if self._w3 and self._w3.is_connected():
            return self._w3

        self._w3 = Web3(Web3.HTTPProvider(self._rpc_url))
        if self.poa:
            self._w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if self._w3.is_connected():
            return self._w3

        raise Exception(f"RPC provider is not connected ({self._rpc_url})")

    @property
    def poa(self):
        return self._poa

    @property
    def account(self):
        return self._account

    def set_account(self, private_key):
        self._account = self.w3.eth.account.from_key(private_key)

    @property
    def contract(self) -> Type[Contract]:
        return self._contract

    def set_contract(self, address, abi):
        self._contract = self.w3.eth.contract(address=address, abi=abi)

    def contract_txn(self, func: Type[ContractFunction]):
        signed_tx = self.build_contract_txn(func)
        txn_hash = self.send_raw_tx(signed_tx)
        return txn_hash.hex()

    def contract_call(self, func: Type[ContractFunction], from_address=None):
        if from_address:
            return func.call({"from": from_address})
        return func.call()

    def build_contract_txn(self, func: Type[ContractFunction]):
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx_data = func.build_transaction({"from": self.account.address, "nonce": nonce})
        return self.sign_tx(tx_data)

    def sign_tx(self, tx_data: TxParams):
        return self.w3.eth.account.sign_transaction(tx_data, self.account.key)

    def send_raw_tx(self, signed_tx):
        return self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    def wait_for_transaction_receipt(self, tx_hash):
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def current_block(self):
        return self.w3.eth.block_number

    def get_transaction_by_hash(self, hash):
        return self.w3.eth.get_transaction(hash)

    def get_transaction_receipt(self, hash):
        return self.w3.eth.get_transaction_receipt(hash)
