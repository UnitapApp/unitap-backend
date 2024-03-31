from authentication.thirdpartydrivers.abstract import BaseThirdPartyDriver
from core.thirdpartyapp import GitcoinPassport


class GitcoinPassportDriver(BaseThirdPartyDriver):
    def submit_passport(self, address: str) -> None | str:
        gp = GitcoinPassport()
        return gp.submit_passport(address)

    def get_score(self, address: str) -> None | tuple:
        gp = GitcoinPassport()
        return gp.get_score(address)
