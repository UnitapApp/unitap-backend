from authentication.thirdpartydrivers.abstract import BaseThirdPartyDriver
from core.thirdpartyapp import LensUtil


class LensDriver(BaseThirdPartyDriver):
    def get_profile_id(self, address):
        lens = LensUtil()
        return lens.get_profile_id(address)
