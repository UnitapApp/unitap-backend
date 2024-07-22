import os

import requests
import tweepy
from ratelimit import limits, sleep_and_retry


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
        self.client = tweepy.Client(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True,
        )

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

    def get_user_id(self) -> str:
        try:
            user_id = self.api.verify_credentials().id_str
        except tweepy.TweepyException as e:
            raise TwitterUtilsError(f"Can not get user_id, error: {e}")
        return user_id

    def get_tweet_count(self) -> int:
        user = self.api.get_user()
        return user.statuses_count

    def get_follower_count(self) -> int:
        user = self.api.get_user()
        return user.followers_count

    def get_is_replied(self, user_tweet_id: str, reference_tweet_id: str) -> bool:
        user_id = self.get_user_id()

        tweet = self.client.get_tweet(
            id=user_tweet_id,
            tweet_fields=["referenced_tweets"],
            user_fields=["id"],
            expansions=["referenced_tweets.id", "author_id"],
            user_auth=True,
        ).data

        if tweet.referenced_tweets:
            for referenced_tweet in tweet.referenced_tweets:
                if (
                    referenced_tweet.type == "replied_to"
                    and referenced_tweet.id == str(reference_tweet_id)
                ):
                    if tweet.author_id == user_id:
                        return True
        return False

    def get_is_liked(self, reference_tweet_id: str) -> bool:
        user_id = self.get_user_id()

        liked_users = self.client.get_liking_users(
            id=reference_tweet_id, user_auth=True
        ).data

        for liker in liked_users:
            if liker.id == user_id:
                return True
        return False

    def did_retweet_tweet(self, tweet_id: str) -> bool:
        user_id = self.get_user_id()
        next_token = None
        attempt = 0

        while True and attempt < 5:
            attempt += 1
            response = self.client.get_retweeters(
                tweet_id, user_auth=True, pagination_token=next_token
            )
            retweeters = response.data
            if retweeters is None:
                return False

            did_retweet = bool(filter(lambda user: user.id == user_id, retweeters))
            if did_retweet:
                return True
            next_token = response.meta.get("next_token")
            if next_token is None:
                return False


class RapidTwitter:
    rapid_key = os.getenv("RAPID_API_KEY")
    host = "twitter135.p.rapidapi.com"

    @sleep_and_retry
    @limits(calls=5, period=1)
    def _request(self, url, params):
        return requests.get(
            url=f"https://{self.host}/{url}",
            headers={"x-rapidapi-key": self.rapid_key, "x-rapidapi-host": self.host},
            params=params,
        )

    def get_user_id(self, username: str):
        response = self._request(url="UserByScreenName", params={"username": username})
        response.raise_for_status()
        return response.json()["data"]["user"]["result"]["rest_id"]

    def is_following(self, username: str, target_username: str):
        target_id = self.get_user_id(target_username)
        cursor = None

        while True:
            response = self._request(
                url="v1.1/FollowingIds",
                params={"username": username, "count": 5000, "cursor": cursor},
            )
            response.raise_for_status()
            data = response.json()
            followings = data["ids"]
            if target_id in followings:
                return True

            cursor = data["next_cursor"]
            if not cursor:
                return False

    def get_followers(self, username: str, cursor=None):
        response = self._request(
            url="v1.1/FollowersIds",
            params={"username": username, "count": 5000, "cursor": cursor},
        )

        response.raise_for_status()

        data = response.json()
        followers = data["ids"]
        cursor = data["next_cursor"]
        if cursor:
            followers += self.get_followers(username, cursor)
        return followers
