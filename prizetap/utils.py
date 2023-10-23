from core.utils import Web3Utils
from faucet.models import Chain
from .constants import (
    PRIZETAP_ERC20_ABI,
    PRIZETAP_ERC721_ABI,
    UNITAP_PASS_ABI,
    VRF_CLIENT_ABI,
    VRF_CLIENT_POLYGON_ADDRESS,
    LINEA_PRIZETAP_ABI
)


class PrizetapContractClient(Web3Utils):
    def __init__(self, raffle) -> None:
        super().__init__(raffle.chain.rpc_url_private, raffle.chain.poa)
        self.raffle = raffle
        abi = PRIZETAP_ERC721_ABI if self.raffle.is_prize_nft else PRIZETAP_ERC20_ABI
        self.set_contract(self.raffle.contract, abi)
        self.set_account(self.raffle.chain.wallet.private_key)

    def draw_raffle(self):
        func = self.contract.functions.heldRaffle(self.raffle.raffleId)
        return self.contract_txn(func)

    def get_raffle_winner(self):
        func = self.contract.functions.raffles(self.raffle.raffleId)
        raffle = self.contract_call(func)
        return raffle[8]
    
class LineaPrizetapContractClient(PrizetapContractClient):
    def __init__(self, raffle) -> None:
        super().__init__(raffle)
        abi = LINEA_PRIZETAP_ABI
        self.set_contract(self.raffle.contract, abi)

    def draw_raffle(self, expiration_time, random_words, reqId, muon_sig, gateway_sig):
        func = self.contract.functions.drawRaffle(
            self.raffle.raffleId,
            expiration_time,
            random_words,
            reqId,
            muon_sig,
            gateway_sig
        )
        return self.contract_txn(func)

    def get_raffle_winners(self):
        func = self.contract.functions.getWinners(self.raffle.raffleId)
        return self.contract_call(func)

    def get_raffle_winners_count(self):
        func = self.contract.functions.raffles(self.raffle.raffleId)
        raffle = self.contract_call(func)
        return raffle[6]

class VRFClientContractClient(Web3Utils):
    def __init__(self, chain) -> None:
        super().__init__(chain.rpc_url_private, chain.poa)
        self.set_contract(VRF_CLIENT_POLYGON_ADDRESS, VRF_CLIENT_ABI)
        self.set_account(chain.wallet.private_key)

    def request_random_words(self, num_words):
        func = self.contract.functions.requestRandomWords(num_words)
        return self.contract_txn(func)


class UnitapPassClient(Web3Utils):
    def __init__(self, chain: Chain) -> None:
        super().__init__(chain.rpc_url_private, chain.poa)
        self.set_contract(
            "0x23826Fd930916718a98A21FF170088FBb4C30803", UNITAP_PASS_ABI)

    def is_holder(self, address: str):
        func = self.contract.functions.balanceOf(address)
        balance = self.contract_call(func)
        return balance != 0
