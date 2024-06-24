from authentication.thirdpartydrivers.abstract import BaseThirdPartyDriver
from core.thirdpartyapp import DiscordUtils


class DiscordDriver(BaseThirdPartyDriver):
    def get_user_guilds(self, access_token: str) -> None | dict:
        return DiscordUtils.get_user_guilds(access_token=access_token)

    def get_user_info(self, access_token: str) -> None | dict:
        return DiscordUtils.get_user_info(access_token=access_token)
