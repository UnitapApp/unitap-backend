from authentication.thirdpartydrivers.abstract import BaseThirdPartyDriver
from core.thirdpartyapp import TwitterUtils


class TwitterDriver(BaseThirdPartyDriver):
    def get_tweet_count(
        self, access_token: str, access_token_secret: str
    ) -> None | str:
        twitter = TwitterUtils(access_token, access_token_secret)
        return twitter.get_tweet_count()

    def get_follower_count(self, access_token: str, access_token_secret: str) -> str:
        twitter = TwitterUtils(access_token, access_token_secret)
        return twitter.get_follower_count()
