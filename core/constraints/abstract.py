import copy
from abc import ABC, abstractmethod
from enum import Enum


class ConstraintApp(Enum):
    GENERAL = "general"
    BRIGHT_ID = "bright_id"
    LENS = "lens"
    FARCASTER = "farcaster"
    ENS = "ENS"
    EAS = "EAS"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


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
    FARCASTER_FID = "farcaster_fid"
    FARCASTER_CAST_HASH = "farcaster_cast_hash"
    KEY = "key"
    VALUE = "value"
    EAS_SCHEMA_ID = "eas_schema_id"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ConstraintVerification(ABC):
    _param_keys = []
    app_name = ConstraintApp.GENERAL.value
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

    @property
    def user_addresses(self):
        from core.models import NetworkTypes

        user_addresses = self.user_profile.wallets.filter(
            wallet_type=NetworkTypes.EVM
        ).values_list("address", flat=True)
        return user_addresses
