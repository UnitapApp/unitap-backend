import copy
import csv
import importlib
from abc import ABC, abstractmethod
from enum import Enum

from django.core.exceptions import ImproperlyConfigured
from django.db.models.functions import Lower

from core.utils import NFTClient


class ConstraintParam(Enum):
    CHAIN = "chain"
    ADDRESS = "address"
    ID = "id"
    USERNAME = "username"
    FROM_DATE = "from_date"
    TO_DATE = "to_date"
    WALLETS_CSV_FILE = "wallets_csv_file"
    COLLECTION_ADDRESS = "collection_address"
    MINIMUM = "minimum"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def is_valid_wallets_csv_file(cls):
        # TODO: fixme
        pass


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
        ConstraintParam.COLLECTION_ADDRESS,
        ConstraintParam.MINIMUM,
    ]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        from core.models import Chain

        chain_id = self._param_values[ConstraintParam.CHAIN.name]
        collection_address = self._param_values[ConstraintParam.COLLECTION_ADDRESS.name]
        minimum = self._param_values[ConstraintParam.MINIMUM.name]

        chain = Chain.objects.get(chain_id=chain_id)
        nft_client = NFTClient(chain=chain, contract=collection_address)

        user_wallets = self.user_profile.wallets.filter(wallet_type=chain.chain_type)

        token_count = 0
        for wallet in user_wallets:
            token_count += nft_client.get_number_of_tokens(
                nft_client.to_checksum_address(wallet.address)
            )

        return token_count >= int(minimum)


class AllowList(ConstraintVerification):
    _param_keys = [ConstraintParam.WALLETS_CSV_FILE]

    def __init__(self, user_profile, response: str = None) -> None:
        super().__init__(user_profile, response)

    def is_observed(self, *args, **kwargs):
        file_path = self._param_values[ConstraintParam.WALLETS_CSV_FILE]
        self.allow_list = []
        with open(file_path, newline="") as f:
            reader = csv.reader(f)
            self.allow_list = list(reader)
            self.allow_list = [a.lower() for a in self.allow_list]
            user_wallets = self.user_profile.wallets.values_list(
                Lower("address"), flat=True
            )
            for wallet in user_wallets:
                if wallet in self.allow_list:
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
