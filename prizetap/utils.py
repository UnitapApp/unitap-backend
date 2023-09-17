from core.utils import Web3Utils
from faucet.models import Chain
from .constants import (
    PRIZETAP_ERC20_ABI,
    PRIZETAP_ERC721_ABI,
    UNITAP_PASS_ABI
)


class PrizetapContractClient(Web3Utils):
    def __init__(self, raffle) -> None:
        super().__init__(raffle.chain.rpc_url_private)
        self.raffle = raffle
        abi = PRIZETAP_ERC721_ABI if self.raffle.is_prize_nft else PRIZETAP_ERC20_ABI
        self.set_contract(self.raffle.contract, abi)
        self.set_account(self.raffle.chain.wallet.private_key)

    def draw_raffle(self):
        func = self.contract.functions.heldRaffle(self.raffle.raffle_id)
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
