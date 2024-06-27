from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)


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
