from authentication.thirdpartydrivers.abstract import BaseThirdPartyDriver
from core.thirdpartyapp import FarcasterUtil


class FarcasterDriver(BaseThirdPartyDriver):
    def get_fid(self, address):
        fa = FarcasterUtil()
        return fa.get_address_fid(address)
