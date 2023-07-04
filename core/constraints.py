from abc import ABC, abstractmethod
from authentication.models import UserProfile

class ConstraintVerification(ABC):
    def __init__(self, user_profile:UserProfile, response:str = None) -> None:
        self.user_profile = user_profile
        self.response_text = response

    @abstractmethod
    def is_observed(self, *args, **kwargs):
        pass

    def response(self) -> str:
        return self.response_text or f"{self.__class__.__name__} constraint is violated"

class BrightIDMeetVerification(ConstraintVerification):
    def is_observed(self, *args, **kwargs):
        return self.user_profile.is_meet_verified


class BrightIDAuraVerification(ConstraintVerification):
    def is_observed(self, *args, **kwargs):
        return self.user_profile.is_aura_verified
    