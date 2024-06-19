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
        farcaster_utils = FarcasterUtil()
        user_address = self.user_addresses
        for address in user_address:
            if farcaster_utils.get_address_fid(address):
                return True
        return False


class IsFollowingFarcasterUser(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_FID]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        farcaster_fid = self.param_values[ConstraintParam.FARCASTER_FID.name]
        farcaster_util = FarcasterUtil()
        user_addresses = self.user_addresses
        for address in user_addresses:
            if farcaster_util.is_following(farcaster_fid, address):
                return True
        return False


class BeFollowedByFarcasterUser(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_FID]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        farcaster_fid = self.param_values[ConstraintParam.FARCASTER_FID.name]
        farcaster_util = FarcasterUtil()
        user_addresses = self.user_addresses
        for address in user_addresses:
            if farcaster_util.be_followed_by(farcaster_fid, address):
                return True
        return False


class DidLikedFarcasterCast(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_CAST_HASH]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        farcaster_util = FarcasterUtil()
        user_addresses = self.user_addresses
        return farcaster_util.did_liked_cast(
            cast_hash=self.param_values[ConstraintParam.FARCASTER_CAST_HASH.name],
            addresses=user_addresses,
        )


class DidRecastFarcasterCast(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_CAST_HASH]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        farcaster_util = FarcasterUtil()
        user_addresses = self.user_addresses
        return farcaster_util.did_recast_cast(
            cast_hash=self.param_values[ConstraintParam.FARCASTER_CAST_HASH.name],
            addresses=user_addresses,
        )


class HasMinimumFarcasterFollower(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        farcaster_util = FarcasterUtil()
        user_addresses = self.user_addresses
        minimum = self.param_values[ConstraintParam.MINIMUM.name]
        for address in user_addresses:
            if int(farcaster_util.get_follower_number(address)) >= int(minimum):
                return True
        return False


# TODO: add following farcaster channel constraint
