import json
import logging

from django.core.cache import cache
from rest_framework.exceptions import PermissionDenied

from authentication.models import UserProfile
from core.constraints import ConstraintVerification, get_constraint
from core.utils import cache_constraint_result

from .helpers import has_credit_left
from .models import ClaimReceipt, TokenDistribution




class SetDistributionTxValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs["user_profile"]
        self.token_distribution: TokenDistribution = kwargs["token_distribution"]

    def is_owner_of_raffle(self):
        if not self.token_distribution.distributor_profile == self.user_profile:
            raise PermissionDenied(
                "You don't have permission to update this token_distribution"
            )

    def is_tx_empty(self):
        if self.token_distribution.tx_hash:
            raise PermissionDenied("This token_distribution is already updated")

    def is_valid(self, data):
        self.is_owner_of_raffle()
        self.is_tx_empty()

        tx_hash = data.get("tx_hash", None)
        if not tx_hash or len(tx_hash) != 66:
            raise PermissionDenied("Tx hash is not valid")




class TokenDistributionValidator:
    def __init__(
        self,
        td: TokenDistribution,
        user_profile: UserProfile,
        td_data: dict,
        *args,
        **kwargs,
    ) -> None:
        self.td = td
        self.td_data = td_data
        self.user_profile = user_profile
        self.request = kwargs.get("request")

    def check_user_permissions(self, raise_exception=True):
        try:
            param_values = json.loads(self.td.constraint_params)
        except Exception as e:
            logging.error("Error parsing constraint params", e)
            param_values = {}
        error_messages = dict()
        result = dict()
        for c in self.td.constraints.all():
            constraint: ConstraintVerification = get_constraint(c.name)(
                self.user_profile, 
            )
            constraint.response = c.response
            try:
                constraint.param_values = param_values[c.name]
            except KeyError:
                pass
            
            cdata = self.td_data.get(str(c.pk), dict())
            cache_key = f"tokentap-{self.user_profile.pk}-{self.td.pk}-{c.pk}"
            constraint_data = cache.get(cache_key)
            if constraint_data is None:
                info = constraint.get_info(
                    **cdata,
                    token_distribution=self.td,
                )
                if str(c.pk) in self.td.reversed_constraints_list:
                    is_verified = not constraint.is_observed(
                        **cdata,
                        token_distribution=self.td,
                    )
                else:
                    is_verified = constraint.is_observed(
                        **cdata,
                        token_distribution=self.td,
                        context={"request": self.request}
                    )

                if constraint.is_cachable:
                    constraint_data = cache_constraint_result(cache_key, is_verified, info)
                else:
                    constraint_data = {"is_verified": is_verified, "info": info}

            if not constraint_data.get("is_verified"):
                error_messages[c.title] = constraint.response
            result[c.pk] = constraint_data
        if len(error_messages) and raise_exception:
            raise PermissionDenied(error_messages)
        return result
    
    def cache_constraint(self):
        pass

    def check_user_credit(self):
        if self.td.is_one_time_claim:
            already_claimed = self.td.claims.filter(
                user_profile=self.user_profile,
                status=ClaimReceipt.VERIFIED,
            ).exists()
            if already_claimed:
                raise PermissionDenied("You have already claimed")
        elif not has_credit_left(self.td, self.user_profile):
            raise PermissionDenied("You have reached your claim limit")

    def check_token_distribution_is_claimable(self):
        if not self.td.is_claimable:
            raise PermissionDenied("This token is not claimable")

    def is_valid(self):
        self.check_user_permissions()
        self.check_token_distribution_is_claimable()
        self.check_user_credit()
