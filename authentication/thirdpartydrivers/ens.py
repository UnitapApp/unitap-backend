from authentication.thirdpartydrivers.abstract import BaseThirdPartyDriver
from core.thirdpartyapp import ENSUtil


class ENSDriver(BaseThirdPartyDriver):
    def get_name(self, address: str) -> None | str:
        ens = ENSUtil()
        return ens.get_name(address)

    def get_address(self, name: str) -> str:
        ens = ENSUtil()
        return ens.get_address(name)
