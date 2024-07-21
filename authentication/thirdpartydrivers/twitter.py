from authentication.thirdpartydrivers.abstract import BaseThirdPartyDriver
from core.thirdpartyapp import TwitterUtils


class TwitterDriver(BaseThirdPartyDriver):
    def get_tweet_count(
        self, access_token: str, access_token_secret: str
    ) -> None | int:
        twitter = TwitterUtils(access_token, access_token_secret)
        return twitter.get_tweet_count()

    def get_follower_count(
        self, access_token: str, access_token_secret: str
    ) -> None | int:
        twitter = TwitterUtils(access_token, access_token_secret)
        return twitter.get_follower_count()

    def get_is_replied(
        self,
        access_token: str,
        access_token_secret: str,
        tweet_id: str,
        target_tweet_id: str,
    ) -> None | bool:
        twitter = TwitterUtils(access_token, access_token_secret)
        return twitter.get_is_replied(tweet_id, target_tweet_id)

    def get_is_liked(
        self, access_token: str, access_token_secret: str, target_tweet_id: str
    ) -> None | bool:
        twitter = TwitterUtils(access_token, access_token_secret)
        return twitter.get_is_liked(target_tweet_id)

    def get_username(self, access_token: str, access_token_secret: str) -> str:
        twitter = TwitterUtils(access_token, access_token_secret)
        return twitter.get_username()
