import logging

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
        from authentication.models import LensConnection

        lens_util = LensUtil()
        try:
            le_connection = LensConnection.get_connection(self.user_profile)
        except LensConnection.DoesNotExist:
            logging("Lens connection not found.")
            return False
        return bool(lens_util.get_profile_id(le_connection.user_wallet_address))


class IsFollowingLensUser(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PROFILE_ID]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import LensConnection

        lens_util = LensUtil()
        prfoile_id = self.param_values[ConstraintParam.LENS_PROFILE_ID.name]
        try:
            le_connection = LensConnection.get_connection(self.user_profile)
        except LensConnection.DoesNotExist:
            logging("Lens connection not found.")
            return False
        return bool(lens_util.is_following(prfoile_id, le_connection))


class BeFollowedByLensUser(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PROFILE_ID]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import LensConnection

        lens_util = LensUtil()
        profile_id = self.param_values[ConstraintParam.LENS_PROFILE_ID.name]
        try:
            le_connection = LensConnection.get_connection(self.user_profile)
        except LensConnection.DoesNotExist:
            logging("Lens connection not found.")
            return False
        return bool(
            lens_util.be_followed_by(profile_id, le_connection.user_wallet_address)
        )


class DidMirrorOnLensPublication(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PUBLICATION_ID]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import LensConnection

        lens_util = LensUtil()
        publication_id = self.param_values[ConstraintParam.LENS_PUBLICATION_ID.name]
        try:
            le_connection = LensConnection.get_connection(self.user_profile)
        except LensConnection.DoesNotExist:
            logging("Lens connection not found.")
            return False
        return bool(
            lens_util.did_mirror_on_publication(
                publication_id, le_connection.user_wallet_address
            )
        )


class DidCollectLensPublication(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PUBLICATION_ID]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import LensConnection

        lens_util = LensUtil()
        publication_id = self.param_values[ConstraintParam.LENS_PUBLICATION_ID.name]
        try:
            le_connection = LensConnection.get_connection(self.user_profile)
        except LensConnection.DoesNotExist:
            logging("Lens connection not found.")
            return False
        return bool(
            lens_util.did_collect_publication(
                publication_id,
                le_connection.user_wallet_address,
            )
        )


class HasMinimumLensFollower(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import LensConnection

        lens_util = LensUtil()
        minimum = int(self.param_values[ConstraintParam.MINIMUM.name])
        try:
            le_connection = LensConnection.get_connection(self.user_profile)
        except LensConnection.DoesNotExist:
            logging("Lens connection not found.")
            return False
        try:
            return (
                lens_util.get_follower_number(le_connection.user_wallet_address)
                >= minimum
            )
        except TypeError:
            return False


class HasMinimumLensPost(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]
    app_name = ConstraintApp.LENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import LensConnection

        lens_util = LensUtil()
        minimum = int(self.param_values[ConstraintParam.MINIMUM.name])
        try:
            le_connection = LensConnection.get_connection(self.user_profile)
        except LensConnection.DoesNotExist:
            logging("Lens connection not found.")
            return False
        try:
            return (
                lens_util.get_post_number(le_connection.user_wallet_address) >= minimum
            )
        except TypeError:
            return False
