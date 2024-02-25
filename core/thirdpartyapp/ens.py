from ens import ENS

from core.utils import Web3Utils


class ENSUtil:
    def __init__(self):
        from core.models import Chain

        self.eth_rpc = Chain.objects.get(chain_id="1")
        self.w3_utils = Web3Utils(rpc_url=self.eth_rpc)

    @property
    def w3(self):
        return self.w3_utils.w3

    @property
    def ns(self) -> ENS:
        return ENS.from_web3(self.w3)

    def get_address(self, name: str) -> str:
        """return address of ENS
        :param name:
        :return: address
        """
        return self.ns.address(name)

    def get_name(self, address: str) -> None | str:
        """return name on address
        :param address:
        """
        _address = self.w3_utils.to_checksum_address(address)
        return self.ns.name(_address)
