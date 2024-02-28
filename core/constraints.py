import copy
import csv
import importlib
from abc import ABC, abstractmethod
from enum import Enum

import rest_framework.exceptions
from django.core.exceptions import ImproperlyConfigured
from django.db.models.functions import Lower

from core.thirdpartyapp import ENSUtil, LensUtil
from core.utils import InvalidAddressException, NFTClient, TokenClient


class ConstraintParam(Enum):
    CHAIN = "chain"
    ADDRESS = "address"
    ID = "id"
    USERNAME = "username"
    FROM_DATE = "from_date"
    TO_DATE = "to_date"
    CSV_FILE = "csv_file"
    MINIMUM = "minimum"
    LENS_PROFILE_ID = "lens_profile_id"
    LENS_PUBLICATION_ID = "lens_publication_id"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ConstraintVerification(ABC):
    _param_keys = []
    __response_text = ""

    def __init__(self, user_profile) -> None:
        self.user_profile = user_profile
        self._param_values = {}

    @abstractmethod
    def is_observed(self, *args, **kwargs) -> bool:
        pass

    @classmethod
    def param_keys(cls) -> list:
        return cls._param_keys

    @property
    def param_values(self):
        return self._param_values

    @param_values.setter
    def param_values(self, values: dict):
        self.is_valid_param_keys(values.keys())
        self._param_values = copy.deepcopy(values)

    @classmethod
    def is_valid_param_keys(cls, keys):
        valid_keys = [key.name for key in cls.param_keys()]
        observed_keys = []
        for key in keys:
            if key not in valid_keys:
                raise KeyError(f"Invalid param key {key}")
            observed_keys.append(key)
        valid_keys.sort()
        observed_keys.sort()
        if valid_keys != observed_keys:
            raise KeyError("Some param keys were not observed")

    @property
    def response(self) -> str:
        return (
            self.__response_text or f"{self.__class__.__name__} constraint is violated"
        )

    @response.setter
    def response(self, text: str):
        self.__response_text = text


class BrightIDMeetVerification(ConstraintVerification):
    def is_observed(self, *args, **kwargs):
        return self.user_profile.is_meet_verified


class BrightIDAuraVerification(ConstraintVerification):
    def is_observed(self, *args, **kwargs):
        return self.user_profile.is_aura_verified


class HasNFTVerification(ConstraintVerification):
    _param_keys = [
        ConstraintParam.CHAIN,
        ConstraintParam.ADDRESS,
        ConstraintParam.MINIMUM,
    ]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        from core.models import Chain

        chain_pk = self._param_values[ConstraintParam.CHAIN.name]
        collection_address = self._param_values[ConstraintParam.ADDRESS.name]
        minimum = self._param_values[ConstraintParam.MINIMUM.name]

        chain = Chain.objects.get(pk=chain_pk)
        nft_client = NFTClient(chain=chain, contract=collection_address)

        user_wallets = self.user_profile.wallets.filter(wallet_type=chain.chain_type)

        token_count = 0
        try:
            for wallet in user_wallets:
                token_count += nft_client.get_number_of_tokens(
                    nft_client.to_checksum_address(wallet.address)
                )
        except InvalidAddressException as e:
            raise rest_framework.exceptions.ValidationError(e)

        return token_count >= int(minimum)


class HasTokenVerification(ConstraintVerification):
    _param_keys = [
        ConstraintParam.CHAIN,
        ConstraintParam.ADDRESS,
        ConstraintParam.MINIMUM,
    ]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        from core.models import Chain

        chain_pk = self._param_values[ConstraintParam.CHAIN.name]
        token_address = self._param_values[ConstraintParam.ADDRESS.name]
        minimum = self._param_values[ConstraintParam.MINIMUM.name]
        is_native_token = False

        if token_address[:4] == "0x00":
            token_address = None
            is_native_token = True

        chain = Chain.objects.get(pk=chain_pk)

        user_wallets = self.user_profile.wallets.filter(wallet_type=chain.chain_type)

        token_client = TokenClient(chain=chain, contract=token_address)

        token_count = 0
        if is_native_token:
            try:
                for wallet in user_wallets:
                    token_count += token_client.get_native_token_balance(
                        token_client.to_checksum_address(wallet.address)
                    )
            except InvalidAddressException as e:
                raise rest_framework.exceptions.ValidationError(e)
        else:
            try:
                for wallet in user_wallets:
                    token_count += token_client.get_non_native_token_balance(
                        token_client.to_checksum_address(wallet.address)
                    )
            except InvalidAddressException as e:
                raise rest_framework.exceptions.ValidationError(e)

        return token_count >= int(minimum)


class AllowListVerification(ConstraintVerification):
    _param_keys = [ConstraintParam.CSV_FILE]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        file_path = self._param_values[ConstraintParam.CSV_FILE.name]
        self.allow_list = []
        with open(file_path, newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            self.allow_list = [a[0].lower() for a in data]
            user_wallets = self.user_profile.wallets.values_list(
                Lower("address"), flat=True
            )
            for wallet in user_wallets:
                if wallet in self.allow_list:
                    return True
            return False


class HasENSVerification(ConstraintVerification):
    _param_keys = []

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        ens_util = ENSUtil()
        for wallet in user_wallets:
            if ens_util.get_name(wallet.address) is not None:
                return True
        return False


class HasLensProfile(ConstraintVerification):
    _param_keys = []

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

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if lens_util.is_following(
                self._param_values[ConstraintParam.LENS_PROFILE_ID.name], wallet.address
            ):
                return True
        return False


class BeFollowedByLensUser(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PROFILE_ID]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if lens_util.be_followed_by(
                self._param_values[ConstraintParam.LENS_PROFILE_ID.name], wallet.address
            ):
                return True
        return False


class DidMirrorOnLensPublication(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PUBLICATION_ID]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if lens_util.did_mirror_on_publication(
                self._param_values[ConstraintParam.LENS_PUBLICATION_ID.name],
                wallet.address,
            ):
                return True
        return False


class DidCollectLensPublication(ConstraintVerification):
    _param_keys = [ConstraintParam.LENS_PUBLICATION_ID]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if lens_util.did_collect_publication(
                self._param_values[ConstraintParam.LENS_PUBLICATION_ID.name],
                wallet.address,
            ):
                return True
        return False


class HasMinimumLensFollower(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if int(lens_util.get_follower_number(wallet.address)) > int(
                self._param_values[ConstraintParam.MINIMUM.name]
            ):
                return True
        return False


class HasMinimumLensPost(ConstraintVerification):
    _param_keys = [ConstraintParam.MINIMUM]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        lens_util = LensUtil()
        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        for wallet in user_wallets:
            if int(lens_util.get_post_number(wallet.address)) > int(
                self._param_values[ConstraintParam.MINIMUM.name]
            ):
                return True
        return False


def get_constraint(constraint_label: str) -> ConstraintVerification:
    app_name, constraint_name = constraint_label.split(".")
    constraints_module_name = f"{app_name}.constraints"
    try:
        constraints_module = importlib.import_module(constraints_module_name)
        constraint_class = getattr(constraints_module, constraint_name)
        return constraint_class
    except (ModuleNotFoundError, AttributeError):
        raise ImproperlyConfigured(
            f"Constraint '{constraint_name}' not found in any app."
        )
