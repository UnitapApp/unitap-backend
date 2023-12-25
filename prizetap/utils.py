import time

from brightIDfaucet.settings import DEPLOYMENT_ENV
from core.models import Chain
from core.utils import Web3Utils

from .constants import (
    PRIZETAP_ERC20_ABI,
    PRIZETAP_ERC721_ABI,
    UNITAP_PASS_ABI,
    VRF_CLIENT_ABI,
    VRF_CLIENT_MUMBAI_ADDRESS,
    VRF_CLIENT_POLYGON_ADDRESS,
)


class PrizetapContractClient:
    def __init__(self, raffle) -> None:
        self.raffle = raffle
        self.web3_utils = Web3Utils(
            self.raffle.chain.rpc_url_private, self.raffle.chain.poa
        )
        abi = PRIZETAP_ERC721_ABI if self.raffle.is_prize_nft else PRIZETAP_ERC20_ABI
        self.web3_utils.set_contract(self.raffle.contract, abi)
        self.web3_utils.set_account(self.raffle.chain.wallet.private_key)

    def set_raffle_random_words(
        self, expiration_time, random_words, reqId, muon_sig, gateway_sig
    ):
        func = self.web3_utils.contract.functions.setRaffleRandomNumbers(
            self.raffle.raffleId,
            expiration_time,
            random_words,
            reqId,
            muon_sig,
            gateway_sig,
        )
        return self.web3_utils.contract_txn(func)

    def get_raffle(self):
        func = self.web3_utils.contract.functions.raffles(self.raffle.raffleId)
        output = self.web3_utils.contract_call(func)
        return self.__process_raffle(output)

    def get_last_winner_index(self):
        raffle = self.get_raffle()
        return raffle["lastWinnerIndex"]

    def set_winners(self):
        winners_count = self.raffle.winners_count
        last_winner_index = self.get_last_winner_index()
        tx_hash = None
        while last_winner_index < winners_count:
            to_id = last_winner_index + 25
            if to_id > winners_count:
                to_id = winners_count
            func = self.web3_utils.contract.functions.setWinners(
                self.raffle.raffleId, to_id
            )
            last_winner_index = to_id
            tx_hash = self.web3_utils.contract_txn(func)
            self.web3_utils.wait_for_transaction_receipt(tx_hash)

        return tx_hash

    def get_raffle_winners(self):
        func = self.web3_utils.contract.functions.getWinners(
            self.raffle.raffleId, 1, self.raffle.winners_count
        )
        return self.web3_utils.contract_call(func)

    def get_raffle_winners_count(self):
        func = self.web3_utils.contract.functions.getWinnersCount(self.raffle.raffleId)
        return self.web3_utils.contract_call(func)

    def __process_raffle(self, output):
        raffles_abi = [
            item
            for item in self.web3_utils.contract.abi
            if item.get("name") == "raffles"
        ]
        assert len(raffles_abi) == 1, "The raffles abi not found"
        raffles_abi = raffles_abi[0]
        result = {}
        for index, item in enumerate(raffles_abi["outputs"]):
            result[item["name"]] = output[index]
        return result

    def get_raffle_created_log(self, receipt):
        return self.web3_utils.contract.events.RaffleCreated().process_receipt(
            receipt, errors=self.web3_utils.LOG_DISCARD
        )[0]


class VRFClientContractClient:
    def __init__(self, chain) -> None:
        self.web3_utils = Web3Utils(chain.rpc_url_private, chain.poa)
        address = (
            VRF_CLIENT_POLYGON_ADDRESS
            if DEPLOYMENT_ENV == "main"
            else VRF_CLIENT_MUMBAI_ADDRESS
        )
        self.web3_utils.set_contract(address, VRF_CLIENT_ABI)
        self.web3_utils.set_account(chain.wallet.private_key)

    def get_last_request_id(self):
        func = self.web3_utils.contract.functions.lastRequestId()
        return self.web3_utils.contract_call(func)

    def get_last_request(self):
        last_id = self.get_last_request_id()
        func = self.web3_utils.contract.functions.vrfRequests(last_id)
        return self.web3_utils.contract_call(func)

    def get_validity_period(self):
        func = self.web3_utils.contract.functions.validityPeriod()
        return self.web3_utils.contract_call(func)

    def request_random_words(self, num_words):
        last_request = self.get_last_request()
        expiration_time = last_request[0]
        now = int(time.time())
        if expiration_time < now:
            func = self.web3_utils.contract.functions.requestRandomWords(num_words)
            return self.web3_utils.contract_txn(func)


class UnitapPassClient:
    def __init__(self, chain: Chain) -> None:
        self.web3_utils = Web3Utils(chain.rpc_url_private, chain.poa)
        self.web3_utils.set_contract(
            "0x23826Fd930916718a98A21FF170088FBb4C30803", UNITAP_PASS_ABI
        )

    def is_holder(self, address: str):
        func = self.web3_utils.contract.functions.balanceOf(address)
        balance = self.web3_utils.contract_call(func)
        return balance != 0

    def to_checksum_address(self, address: str):
        return self.web3_utils.w3.to_checksum_address(address)
