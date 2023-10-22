from core.constraints import *
from core.utils import TimeUtils
from faucet.constraints import OptimismHasClaimedGasInThisRound
from faucet.models import ClaimReceipt


class OncePerWeekVerification(ConstraintVerification):
    def is_observed(self, *args, **kwargs):
        token_distribution = kwargs["token_distribution"]
        return not token_distribution.claims.filter(
            user_profile=self.user_profile,
            created_at__gte=TimeUtils.get_last_monday(),
        ).exists()


class OncePerMonthVerification(ConstraintVerification):
    def is_observed(self, *args, **kwargs):
        token_distribution = kwargs["token_distribution"]
        return not token_distribution.claims.filter(
            user_profile=self.user_profile,
            created_at__gte=TimeUtils.get_first_day_of_the_month(),
        ).exists()


class OnceInALifeTimeVerification(ConstraintVerification):
    def is_observed(self, *args, **kwargs):
        token_distribution = kwargs["token_distribution"]
        return not token_distribution.claims.filter(
            user_profile=self.user_profile,
            status=ClaimReceipt.VERIFIED,
        ).exists()
