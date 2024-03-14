from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.thirdpartyapp import FarcasterUtil


class HasFarcasterProfile(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        farcaster_utils = FarcasterUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if farcaster_utils.get_address_fid(wallet.address):
                return True
        return False


class IsFollowingFarcasterUser(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_FID]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        farcaster_util = FarcasterUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if farcaster_util.is_following(
                self._param_values[ConstraintParam.FARCASTER_FID.name], wallet.address
            ):
                return True
        return False


class BeFollowedByFarcasterUser(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_FID]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        farcaster_util = FarcasterUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if farcaster_util.be_followed_by(
                self._param_values[ConstraintParam.FARCASTER_FID.name], wallet.address
            ):
                return True
        return False


class DidLikedFarcasterCast(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_CAST_HASH]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        farcaster_util = FarcasterUtil()
        user_addresses = self.user_profile.wallets.filter(
            wallet_type=NetworkTypes.EVM
        ).values_list("address", flat=True)
        return farcaster_util.did_liked_cast(
            cast_hash=self._param_values[ConstraintParam.FARCASTER_CAST_HASH.name],
            addresses=user_addresses,
        )


class DidRecastFarcasterCast(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_CAST_HASH]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        farcaster_util = FarcasterUtil()
        user_addresses = self.user_profile.wallets.filter(
            wallet_type=NetworkTypes.EVM
        ).values_list("address", flat=True)
        return farcaster_util.did_recast_cast(
            cast_hash=self._param_values[ConstraintParam.FARCASTER_CAST_HASH.name],
            addresses=user_addresses,
        )


class HasMinimumFarcasterFollower(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        farcaster_util = FarcasterUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if int(farcaster_util.get_follower_number(wallet.address)) > int(
                self._param_values[ConstraintParam.MINIMUM.name]
            ):
                return True
        return False


# TODO: add following farcaster channel constraint
