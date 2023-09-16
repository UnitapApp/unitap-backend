import datetime
import pytz
from time import time
from web3 import Web3
from web3.contract.contract import Contract, ContractFunction
from web3.types import Type, TxParams
from django.utils import timezone


class TimeUtils:
    @staticmethod
    def get_last_monday():
        now = int(time())
        day = 86400  # seconds in a day
        week = 7 * day
        weeks = now // week  # number of weeks since epoch
        monday = 345600  # first monday midnight
        last_monday_midnight = monday + (weeks * week)

        # last monday could be off by one week
        if last_monday_midnight > now:
            last_monday_midnight -= week

        return timezone.make_aware(
            datetime.datetime.fromtimestamp(last_monday_midnight)
        )

    @staticmethod
    def get_second_last_monday():
        now = int(time())
        day = 86400  # seconds in a day
        week = 7 * day
        weeks = now // week  # number of weeks since epoch
        monday = 345600  # first monday midnight
        last_monday_midnight = monday + (weeks * week)

        # last monday could be off by one week
        if last_monday_midnight > now:
            last_monday_midnight -= week

        return timezone.make_aware(
            datetime.datetime.fromtimestamp(last_monday_midnight - week)
        )

    @staticmethod
    def get_first_day_of_the_month():
        now = datetime.datetime.now(pytz.timezone("UTC"))
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return first_day


class Web3Utils:
    def __init__(self, rpc_url) -> None:
        self._rpc_url = rpc_url
        self._w3 = None
        self._account = None
        self._contract = None

    @property
    def w3(self) -> Web3:
        if self._w3 and self._w3.is_connected():
            return self._w3

        self._w3 = Web3(Web3.HTTPProvider(self._rpc_url))

        if self._w3.is_connected():
            return self._w3

        raise Exception(f"RPC provider is not connected ({self._rpc_url})")

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
        signed_tx = self.build_contract_call(func)
        txn_hash = self.send_raw_tx(signed_tx)
        return txn_hash.hex()

    def contract_call(self, func: Type[ContractFunction], from_address=None):
        if from_address:
            return func.call({"from": from_address})
        return func.call()

    def build_contract_call(self, func: Type[ContractFunction]):
        tx_data = func.build_transaction({"from": self.account.address})
        return self.sign_tx(tx_data)

    def sign_tx(self, tx_data: TxParams):
        return self.w3.eth.account.sign_transaction(tx_data, self.account.key)

    def send_raw_tx(self, signed_tx):
        return self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
