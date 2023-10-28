from django.db import models
from polymorphic.models import PolymorphicModel

from faucet.faucet_manager.credit_strategy import RoundCreditStrategy


class Permission(PolymorphicModel):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    def is_valid(self, *args, **kwargs):
        # Override this method in subclasses
        return False

    def __str__(self):
        return self.name


class BrightIDMeetVerification(Permission):
    def is_valid(self, user_profile, *args, **kwargs):
        return user_profile.is_meet_verified

    def response(self):
        return "You must be verified on BrightID to claim this token."


class BrightIDAuraVerification(Permission):
    def is_valid(self, user_profile, *args, **kwargs):
        return user_profile.is_aura_verified

    def response(self):
        return "You must be Aura verified on BrightID to claim this token."


class OncePerWeekVerification(Permission):
    def is_valid(self, user_profile, *args, **kwargs):
        token_distribution = kwargs.get("token_distribution")
        return not token_distribution.claims.filter(
            user_profile=user_profile,
            created_at__gte=RoundCreditStrategy.get_start_of_the_round(),
        ).exists()

    def response(self):
        return "You have already claimed this token this week"


class OncePerMonthVerification(Permission):
    def is_valid(self, user_profile, *args, **kwargs):
        token_distribution = kwargs.get("token_distribution")
        return not token_distribution.claims.filter(
            user_profile=user_profile,
            created_at__gte=RoundCreditStrategy.get_start_of_the_round(),
        ).exists()

    def response(self):
        return "You have already claimed this token this month"


class OnceInALifeTimeVerification(Permission):
    def is_valid(self, user_profile, *args, **kwargs):
        token_distribution = kwargs.get("token_distribution")
        return not token_distribution.claims.filter(
            user_profile=user_profile,
        ).exists()

    def response(self):
        return "You have already claimed this token"


# class WhitelistVerification(Permission):
#     def is_valid(self, user_profile, *args, **kwargs):
#         if user_profile.wallets.filter(wallet_type="EVM").exists():
#             return user_profile.wallets.filter(wallet_type="EVM").first().address in []
#         return False
