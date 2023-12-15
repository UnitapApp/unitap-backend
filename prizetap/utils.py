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


class PrizetapContractClient(Web3Utils):
    def __init__(self, raffle) -> None:
        super().__init__(raffle.chain.rpc_url_private, raffle.chain.poa)
        self.raffle = raffle
        abi = PRIZETAP_ERC721_ABI if self.raffle.is_prize_nft else PRIZETAP_ERC20_ABI
        self.set_contract(self.raffle.contract, abi)
        self.set_account(self.raffle.chain.wallet.private_key)

    def set_raffle_random_words(
        self, expiration_time, random_words, reqId, muon_sig, gateway_sig
    ):
        func = self.contract.functions.setRaffleRandomNumbers(
            self.raffle.raffleId,
            expiration_time,
            random_words,
            reqId,
            muon_sig,
            gateway_sig,
        )
        return self.contract_txn(func)

    def get_raffle(self):
        func = self.contract.functions.raffles(self.raffle.raffleId)
        output = self.contract_call(func)
        return self.__process_raffle(output)

    def get_last_winner_index(self):
        raffle = self.get_raffle()
        return raffle["lastWinnerIndex"]

    def set_winners(self):
        winners_count = self.raffle.winners_count
        last_winner_index = self.get_last_winner_index()
        while last_winner_index < winners_count:
            to_id = last_winner_index + 25
            if to_id > winners_count:
                to_id = winners_count
            func = self.contract.functions.setWinners(self.raffle.raffleId, to_id)
            last_winner_index = to_id
            tx_hash = self.contract_txn(func)
            self.wait_for_transaction_receipt(tx_hash)

        return tx_hash

    def get_raffle_winners(self):
        func = self.contract.functions.getWinners(
            self.raffle.raffleId, 1, self.raffle.winners_count
        )
        return self.contract_call(func)

    def get_raffle_winners_count(self):
        func = self.contract.functions.getWinnersCount(self.raffle.raffleId)
        return self.contract_call(func)

    def __process_raffle(self, output):
        raffles_abi = [
            item for item in self.contract.abi if item.get("name") == "raffles"
        ]
        assert len(raffles_abi) == 1, "The raffles abi not found"
        raffles_abi = raffles_abi[0]
        result = {}
        for index, item in enumerate(raffles_abi["outputs"]):
            result[item["name"]] = output[index]
        return result


class VRFClientContractClient(Web3Utils):
    def __init__(self, chain) -> None:
        super().__init__(chain.rpc_url_private, chain.poa)
        address = (
            VRF_CLIENT_POLYGON_ADDRESS
            if DEPLOYMENT_ENV == "main"
            else VRF_CLIENT_MUMBAI_ADDRESS
        )
        self.set_contract(address, VRF_CLIENT_ABI)
        self.set_account(chain.wallet.private_key)

    def get_last_request_id(self):
        func = self.contract.functions.lastRequestId()
        return self.contract_call(func)

    def get_last_request(self):
        last_id = self.get_last_request_id()
        func = self.contract.functions.vrfRequests(last_id)
        return self.contract_call(func)

    def get_validity_period(self):
        func = self.contract.functions.validityPeriod()
        return self.contract_call(func)

    def request_random_words(self, num_words):
        last_request = self.get_last_request()
        expiration_time = last_request[0]
        now = int(time.time())
        if expiration_time < now:
            func = self.contract.functions.requestRandomWords(num_words)
            return self.contract_txn(func)


class UnitapPassClient(Web3Utils):
    def __init__(self, chain: Chain) -> None:
        super().__init__(chain.rpc_url_private, chain.poa)
        self.set_contract("0x23826Fd930916718a98A21FF170088FBb4C30803", UNITAP_PASS_ABI)

    def is_holder(self, address: str):
        func = self.contract.functions.balanceOf(address)
        balance = self.contract_call(func)
        return balance != 0
