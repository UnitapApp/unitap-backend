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
        try:
            follower_count = twitter.driver.get_follower_count()
        except Exception:
            return False
        if follower_count >= int(self.param_values[ConstraintParam.MINIMUM.name]):
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
        try:
            tweet_count = twitter.driver.get_tweet_count()
        except Exception:
            return False
        if tweet_count >= int(self.param_values[ConstraintParam.MINIMUM.name]):
            return True
        return False
