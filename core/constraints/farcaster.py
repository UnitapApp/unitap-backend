import logging

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
        from authentication.models import FarcasterConnection

        try:
            fa_connection = FarcasterConnection.get_connection(self.user_profile)
        except FarcasterConnection.DoesNotExist:
            logging("Farcaster connection not found.")
            return False
        return fa_connection.is_connected()


class IsFollowingFarcasterUser(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_FID]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import FarcasterConnection

        farcaster_fid = self.param_values[ConstraintParam.FARCASTER_FID.name]
        farcaster_util = FarcasterUtil()
        try:
            fa_connection = FarcasterConnection.get_connection(self.user_profile)
        except FarcasterConnection.DoesNotExist:
            logging.error("Farcaster connection not found.")
            return False
        return farcaster_util.is_following(
            farcaster_fid, fa_connection.user_wallet_address
        )


class BeFollowedByFarcasterUser(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_FID]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import FarcasterConnection

        farcaster_fid = self.param_values[ConstraintParam.FARCASTER_FID.name]
        farcaster_util = FarcasterUtil()
        try:
            fa_connection = FarcasterConnection.get_connection(self.user_profile)
        except FarcasterConnection.DoesNotExist:
            logging.error("Farcaster connection not found.")
            return False
        return farcaster_util.be_followed_by(
            farcaster_fid, fa_connection.user_wallet_address
        )


class DidLikedFarcasterCast(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_CAST_HASH]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import FarcasterConnection

        farcaster_util = FarcasterUtil()
        try:
            fa_connection = FarcasterConnection.get_connection(self.user_profile)
        except FarcasterConnection.DoesNotExist:
            logging.error("Farcaster connection not found.")
            return False
        return farcaster_util.did_liked_cast(
            cast_hash=self.param_values[ConstraintParam.FARCASTER_CAST_HASH.name],
            addresses=[
                fa_connection.user_wallet_address,
            ],
        )


class DidRecastFarcasterCast(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_CAST_HASH]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import FarcasterConnection

        farcaster_util = FarcasterUtil()
        try:
            fa_connection = FarcasterConnection.get_connection(self.user_profile)
        except FarcasterConnection.DoesNotExist:
            logging.error("Farcaster connection not found.")
            return False
        return farcaster_util.did_recast_cast(
            cast_hash=self.param_values[ConstraintParam.FARCASTER_CAST_HASH.name],
            addresses=[
                fa_connection.user_wallet_address,
            ],
        )


class HasMinimumFarcasterFollower(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import FarcasterConnection

        farcaster_util = FarcasterUtil()
        try:
            fa_connection = FarcasterConnection.get_connection(self.user_profile)
        except FarcasterConnection.DoesNotExist:
            logging("Farcaster connection not found.")
            return False
        minimum = self.param_values[ConstraintParam.MINIMUM.name]
        try:
            return farcaster_util.get_follower_number(
                fa_connection.user_wallet_address
            ) >= int(minimum)
        except TypeError as e:
            logging.error(f"Can not compare two value: {str(e)}")
            return False


class IsFollowingFarcasterChannel(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_CHANNEL_ID]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import FarcasterConnection

        farcaster_util = FarcasterUtil()
        try:
            fa_connection = FarcasterConnection.get_connection(self.user_profile)
        except FarcasterConnection.DoesNotExist:
            logging.error("Farcaster connection not found.")
            return False
        channel_id = self.param_values[ConstraintParam.FARCASTER_CHANNEL_ID.name]
        return farcaster_util.is_following_channel(
            channel_id=channel_id,
            addresses=[
                fa_connection.user_wallet_address,
            ],
        )


class IsFollowingFarcasterBatch(ConstraintVerification):
    _param_keys = [ConstraintParam.FARCASTER_FIDS]
    app_name = ConstraintApp.FARCASTER.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def get_info(self, *args, **kwargs) -> dict:
        from authentication.models import FarcasterConnection

        farcaster_util = FarcasterUtil()
        try:
            fa_connection = FarcasterConnection.get_connection(self.user_profile)
        except FarcasterConnection.DoesNotExist:
            logging.error("Farcaster connection not found.")
            return None
        fids = self.param_values[ConstraintParam.FARCASTER_FIDS.name]
        return farcaster_util.is_following_batch(
            fids=fids, address=fa_connection.user_wallet_address
        )

    def is_observed(self, *args, **kwargs) -> bool:
        res = self.get_info(*args, **kwargs)
        if res is None:
            return False
        return all(res.values())
