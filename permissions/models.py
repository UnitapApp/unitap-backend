from django.db import models
from polymorphic.models import PolymorphicModel


class Permission(PolymorphicModel):

    name = models.CharField(max_length=200)

    def is_valid(self, *args, **kwargs):
        # Override this method in subclasses
        return False

    def __str__(self):
        return self.name


class BrightIDMeetVerification(Permission):
    def is_valid(self, user_profile, *args, **kwargs):
        return user_profile.is_meet_verified


class BrightIDAuraVerification(Permission):
    def is_valid(self, user_profile, *args, **kwargs):
        return user_profile.is_aura_verified
