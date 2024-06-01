import os

import tweepy


class TwitterUtilsError(tweepy.TweepyException):
    pass


class TwitterUtils:
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    callback_url = os.getenv("TWITTER_CALLBACK_URL")

    def __init__(self, access_token: str, access_token_secret: str):
        auth = tweepy.OAuthHandler(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
        self.api = tweepy.API(auth)

    @classmethod
    def get_authorization_url_and_token(cls) -> tuple:
        auth = tweepy.OAuth1UserHandler(
            consumer_key=cls.consumer_key,
            consumer_secret=cls.consumer_secret,
            callback=cls.callback_url,
        )
        try:
            url = auth.get_authorization_url()
        except tweepy.TweepyException as e:
            raise TwitterUtilsError(f"Can not get authorization token, error: {e}")

        request_token = auth.request_token.copy()

        return url, request_token

    @classmethod
    def get_access_token(
        cls, oauth_token: str, oauth_token_secret: str, oauth_verifier: str
    ) -> tuple:
        auth = tweepy.OAuth1UserHandler(
            consumer_key=cls.consumer_key, consumer_secret=cls.consumer_secret
        )
        auth.request_token = {
            "oauth_token": oauth_token,
            "oauth_token_secret": oauth_token_secret,
        }
        try:
            access_token, access_token_secret = auth.get_access_token(
                verifier=oauth_verifier
            )
        except tweepy.TweepyException as e:
            raise TwitterUtilsError(f"Can not get access token token, error: {e}")

        return access_token, access_token_secret

    def get_username(self) -> str:
        try:
            username = self.api.verify_credentials().screen_name
        except tweepy.TweepyException as e:
            raise TwitterUtilsError(f"Can not get username, error: {e}")
        return username

    def get_tweet_count(self) -> int:
        username = self.get_username()
        user = self.api.get_user(username)
        return user.followers_count

    def get_follower_count(self) -> int:
        username = self.get_username()
        user = self.api.get_user(username)
        return user.statuses_count
