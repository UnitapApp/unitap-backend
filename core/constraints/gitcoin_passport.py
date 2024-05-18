from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)


class HasGitcoinPassportProfile(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GITCOIN_PASSPORT.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import GitcoinPassportConnection

        user_profile = self.user_profile
        try:
            gitcoint_passport = GitcoinPassportConnection.objects.get(
                user_profile=user_profile
            )
        except GitcoinPassportConnection.DoesNotExist:
            return False
        if gitcoint_passport:
            return True
        return False


class HasMinimumHumanityScore(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.GITCOIN_PASSPORT.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import GitcoinPassportConnection

        user_profile = self.user_profile
        try:
            gitcoint_passport = GitcoinPassportConnection.objects.get(
                user_profile=user_profile
            )
        except GitcoinPassportConnection.DoesNotExist:
            return False
        if int(gitcoint_passport.score) >= int(
            self.param_values[ConstraintParam.MINIMUM.name]
        ):
            return True
        return False
