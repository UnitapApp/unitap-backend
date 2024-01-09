import datetime
import logging
import time
from contextlib import contextmanager

import pytz
from django.core.cache import cache
from eth_account.messages import encode_defunct
from solana.rpc.api import Client
from web3 import Account, Web3
from web3.contract.contract import Contract, ContractFunction
from web3.logs import DISCARD, IGNORE, STRICT, WARN
from web3.middleware import geth_poa_middleware
from web3.types import TxParams, Type


@contextmanager
def memcache_lock(lock_id, oid, lock_expire=60):
    timeout_at = time.monotonic() + lock_expire
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, lock_expire)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


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
        first_day_of_last_month = last_month.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        return first_day_of_last_month


class Web3Utils:
    LOG_STRICT = STRICT
    LOG_IGNORE = IGNORE
    LOG_DISCARD = DISCARD
    LOG_WARN = WARN

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

    def get_contract_function(self, func_name: str):
        func = getattr(self.contract.functions, func_name)
        return func

    def contract_txn(self, func: Type[ContractFunction], **kwargs):
        signed_tx = self.build_contract_txn(func, **kwargs)
        txn_hash = self.send_raw_tx(signed_tx)
        return txn_hash.hex()

    def contract_call(self, func: Type[ContractFunction], from_address=None):
        if from_address:
            return func.call({"from": from_address})
        return func.call()

    def get_gas_estimate(self, func: Type[ContractFunction]):
        return func.estimate_gas({"from": self.account.address})

    def build_contract_txn(self, func: Type[ContractFunction], **kwargs):
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx_data = func.build_transaction(
            {"from": self.account.address, "nonce": nonce, **kwargs}
        )
        return self.sign_tx(tx_data)

    def sign_tx(self, tx_data: TxParams):
        return self.w3.eth.account.sign_transaction(tx_data, self.account.key)

    def send_raw_tx(self, signed_tx):
        return self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    def wait_for_transaction_receipt(self, tx_hash):
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def current_block(self):
        return self.w3.eth.block_number

    def get_transaction_by_hash(self, tx_hash):
        return self.w3.eth.get_transaction(tx_hash)

    def get_gas_price(self):
        return self.w3.eth.gas_price

    def from_wei(self, value: int, unit: str = "ether"):
        return self.w3.from_wei(value, unit)

    @staticmethod
    def to_checksum_address(address: str):
        return Web3.to_checksum_address(address.lower())

    @staticmethod
    def hash_message(address, token, amount, nonce):
        message_hash = Web3().solidity_keccak(
            ["address", "address", "uint256", "uint32"],
            [
                Web3.to_checksum_address(address),
                Web3.to_checksum_address(token),
                amount,
                nonce,
            ],
        )
        hashed_message = encode_defunct(hexstr=message_hash.hex())

        return hashed_message

    @staticmethod
    def sign_hashed_message(private_key, hashed_message):
        account = Account.from_key(private_key)
        signed_message = account.sign_message(hashed_message)
        return signed_message.signature.hex()

    def get_transaction_receipt(self, tx_hash):
        return self.w3.eth.get_transaction_receipt(tx_hash)

    def get_balance(self, address):
        return self.w3.eth.get_balance(address)


class SolanaWeb3Utils:
    def __init__(self, rpc_url) -> None:
        self.rpc_url = rpc_url

    @property
    def w3(self) -> Client:
        assert self.rpc_url is not None
        try:
            _w3 = Client(self.rpc_url)
            if _w3.is_connected():
                return _w3
        except Exception as e:
            logging.error(e)
            raise (f"Could not connect to rpc {self.rpc_url}")
