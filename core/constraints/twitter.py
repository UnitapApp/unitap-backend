import logging

from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.thirdpartyapp import RapidTwitter, TwitterUtils


class HasTwitter(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.TWITTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import TwitterConnection

        try:
            twitter = TwitterConnection.get_connection(self.user_profile)
        except TwitterConnection.DoesNotExist:
            return False
        return twitter.is_connected()


class HasMinimumTwitterFollowerCount(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.TWITTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import TwitterConnection

        try:
            twitter = TwitterConnection.get_connection(self.user_profile)
        except TwitterConnection.DoesNotExist:
            return False

        if twitter.follower_count >= int(
            self.param_values[ConstraintParam.MINIMUM.name]
        ):
            return True
        return False


class HasMinimumTweetCount(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.TWITTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import TwitterConnection

        try:
            twitter = TwitterConnection.get_connection(self.user_profile)
        except TwitterConnection.DoesNotExist:
            return False

        if twitter.tweet_count >= int(self.param_values[ConstraintParam.MINIMUM.name]):
            return True
        return False


class HasVoteOnATweet(ConstraintVerification):
    _param_keys = [ConstraintParam.TARGET_TWEET_ID]
    app_name = ConstraintApp.TWITTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import TwitterConnection

        try:
            twitter = TwitterConnection.get_connection(self.user_profile)
        except TwitterConnection.DoesNotExist:
            return False

        if twitter.is_liked(
            target_tweet_id=self.param_values[ConstraintParam.TARGET_TWEET_ID.name]
        ):
            return True
        return False


class HasCommentOnATweet(ConstraintVerification):
    _param_keys = [ConstraintParam.TARGET_TWEET_ID]
    app_name = ConstraintApp.TWITTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import TwitterConnection

        try:
            twitter = TwitterConnection.get_connection(self.user_profile)
        except TwitterConnection.DoesNotExist:
            return False

        self_tweet_id: str = kwargs["tweet_id"] if "tweet_id" in kwargs else None
        if not self_tweet_id:
            return False

        if twitter.is_replied(
            self_tweet_id=self_tweet_id,
            target_tweet_id=self.param_values[ConstraintParam.TARGET_TWEET_ID.name],
        ):
            return True
        return False


class IsFollowinTwitterUser(ConstraintVerification):
    _param_keys = [ConstraintParam.TWITTER_USERNAME]
    app_name = ConstraintApp.TWITTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import TwitterConnection

        try:
            twitter = TwitterConnection.get_connection(self.user_profile)
        except TwitterConnection.DoesNotExist:
            return False

        twitter_username = twitter.username
        rapid_twitter = RapidTwitter()
        try:
            return rapid_twitter.is_following(
                twitter_username,
                self.param_values[ConstraintParam.TWITTER_USERNAME.name],
            )
        except Exception as e:
            logging.error(f"Error in rapid_twitter: {e}")


class BeFollowedByTwitterUser(ConstraintVerification):
    _param_keys = [ConstraintParam.TWITTER_USERNAME]
    app_name = ConstraintApp.TWITTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import TwitterConnection

        try:
            twitter = TwitterConnection.get_connection(self.user_profile)
        except TwitterConnection.DoesNotExist:
            return False

        twitter_username = twitter.username
        rapid_twitter = RapidTwitter()
        try:
            return rapid_twitter.is_following(
                rapid_twitter.is_following(
                    self.param_values[ConstraintParam.TWITTER_USERNAME.name]
                ),
                twitter_username,
            )
        except Exception as e:
            logging.error(f"Error in rapid_twitter: {e}")


class DidRetweetTweet(ConstraintVerification):
    _param_keys = [ConstraintParam.TWEET_ID]
    app_name = ConstraintApp.TWITTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import TwitterConnection

        try:
            twitter = TwitterConnection.get_connection(self.user_profile)
        except TwitterConnection.DoesNotExist:
            return False
        tweet_id = self.param_values[ConstraintParam.TWEET_ID.name]
        twitter_util = TwitterUtils(twitter.access_token, twitter.access_token_secret)
        try:
            return twitter_util.did_retweet_tweet(tweet_id=tweet_id)
        except Exception as e:
            logging.error(f"Error in rapid_twitter: {e}")
