from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.thirdpartyapp import GitcoinPassport
from authentication.models import GitcoinPassportConnection


class HasGitcoinPassportProfile(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.GITCOIN_PASSPORT.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        user_profile = self.user_profile
        if GitcoinPassportConnection.is_connected(user_profile=user_profile):
                return True
        return False


class HasMinimumHumanityScore(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.GITCOIN_PASSPORT.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        gitcoin_passport_utils = GitcoinPassport()
        user_address = self.user_addresses
        for address in user_address:
            if int(gitcoin_passport_utils.get_score(address)[0]) >= int(
                self.param_values[ConstraintParam.MINIMUM.name]
            ):
                return True
        return False
