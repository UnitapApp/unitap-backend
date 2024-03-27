from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.thirdpartyapp import LensUtil


class HasLensProfile(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if lens_util.get_profile_id(wallet.address):
                return True
        return False


class IsFollowingLensUser(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PROFILE_ID]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if lens_util.is_following(
                self.param_values[ConstraintParam.LENS_PROFILE_ID.name], wallet.address
            ):
                return True
        return False


class BeFollowedByLensUser(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PROFILE_ID]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if lens_util.be_followed_by(
                self.param_values[ConstraintParam.LENS_PROFILE_ID.name], wallet.address
            ):
                return True
        return False


class DidMirrorOnLensPublication(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PUBLICATION_ID]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if lens_util.did_mirror_on_publication(
                self.param_values[ConstraintParam.LENS_PUBLICATION_ID.name],
                wallet.address,
            ):
                return True
        return False


class DidCollectLensPublication(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PUBLICATION_ID]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if lens_util.did_collect_publication(
                self.param_values[ConstraintParam.LENS_PUBLICATION_ID.name],
                wallet.address,
            ):
                return True
        return False


class HasMinimumLensFollower(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if int(lens_util.get_follower_number(wallet.address)) > int(
                self.param_values[ConstraintParam.MINIMUM.name]
            ):
                return True
        return False


class HasMinimumLensPost(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if int(lens_util.get_post_number(wallet.address)) > int(
                self.param_values[ConstraintParam.MINIMUM.name]
            ):
                return True
        return False
