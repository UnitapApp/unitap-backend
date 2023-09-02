import copy
from enum import Enum
from abc import ABC, abstractmethod
from authentication.models import UserProfile

class ConstraintParam(Enum):
    CHAIN='chain'
    ADDRESS='address'
    ID='id'
    USERNAME='username'
    FROM_DATE='from_date'
    TO_DATE='to_date'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class ConstraintVerification(ABC):
    _param_keys = []
    _param_values = {}
    __response_text = ""
    
    def __init__(self, user_profile:UserProfile) -> None:
        self.user_profile = user_profile

    @abstractmethod
    def is_observed(self, *args, **kwargs) -> bool:
        pass

    @classmethod
    def param_keys(cls) -> list:
        return cls._param_keys
    
    @classmethod
    def set_param_values(cls, values: dict):
        valid_keys = [key for key in cls.param_keys()]
        for key in values:
            if key not in valid_keys:
                raise Exception(f"Invalid param key {key}")
        cls._param_values = copy.deepcopy(values)

    @property
    def response(self) -> str:
        return self.__response_text or f"{self.__class__.__name__} constraint is violated"
    
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
        ConstraintParam.ID
    ]

    def __init__(self, user_profile: UserProfile, response: str = None) -> None:
        super().__init__(user_profile, response)

    def is_observed(self, *args, **kwargs):
        chain_id = self._param_values[ConstraintParam.CHAIN]
        collection = self._param_values[ConstraintParam.ADDRESS]
        nft_id = self._param_values[ConstraintParam.ID]
    