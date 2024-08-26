import json
import time

from django.core.cache import cache
from rest_framework.exceptions import PermissionDenied, ValidationError

from authentication.models import UserProfile
from core.constraints import ConstraintVerification, get_constraint

from .models import Raffle, RaffleEntry


class RaffleEnrollmentValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs["user_profile"]
        self.raffle: Raffle = kwargs["raffle"]
        self.raffle_data: dict = kwargs.get("raffle_data", dict())
        self.request = kwargs.get("request")

    def can_enroll_in_raffle(self):
        if not self.raffle.is_claimable:
            raise PermissionDenied("Can't enroll in this raffle")

    def check_user_constraints(self, raise_exception=True):
        try:
            param_values = json.loads(self.raffle.constraint_params)
        except Exception:
            param_values = {}
        error_messages = dict()
        result = dict()
        for c in self.raffle.constraints.all():
            constraint: ConstraintVerification = get_constraint(c.name)(
                self.user_profile
            )
            constraint.response = c.response
            try:
                constraint.param_values = param_values[c.name]
            except KeyError:
                pass
            cdata = self.raffle_data.get(str(c.pk), dict())
            cache_key = f"prizetap-{self.user_profile.pk}-{self.raffle.pk}-{c.pk}"
            cache_data = cache.get(cache_key)
            if cache_data is None:
                """
                Refactor: this is not good design beacuse info is duplicated with
                is_observed so we need some design change for in is_observed so
                if info needed it must return it.
                or more basical change likes change how constraints logic is.
                """
                info = constraint.get_info(
                    **cdata, from_time=int(self.raffle.start_at.timestamp())
                )
                if str(c.pk) in self.raffle.reversed_constraints_list:
                    is_verified = not constraint.is_observed(
                        **cdata, from_time=int(self.raffle.start_at.timestamp())
                    )
                else:
                    is_verified = constraint.is_observed(
                        **cdata, from_time=int(self.raffle.start_at.timestamp()), context={"request": self.request}
                    )
                caching_time = 60 * 60 if is_verified else 60
                expiration_time = time.time() + caching_time
                cache_data = {
                    "is_verified": is_verified,
                    "info": info,
                    "expiration_time": expiration_time,
                }
                cache.set(
                    cache_key,
                    cache_data,
                    caching_time,
                )
            if not cache_data.get("is_verified"):
                error_messages[c.title] = constraint.response
            result[c.pk] = cache_data
        if len(error_messages) and raise_exception:
            raise PermissionDenied(error_messages)
        return result

    def check_user_owns_wallet(self, user_wallet_address):
        if not self.user_profile.owns_wallet(user_wallet_address):
            raise PermissionDenied("This wallet is not registered for this user")

    def check_prizetap_winning_chance(self, prizetap_winning_chance_number):
        if prizetap_winning_chance_number > 2:
            raise ValidationError("Winning chance could not be more than 2.")

        if prizetap_winning_chance_number < 0:
            raise ValidationError("Winning chance could not be negative.")

        if (
            prizetap_winning_chance_number
            > self.user_profile.prizetap_winning_chance_number
        ):
            raise ValidationError("Insufficient winning chances available.")

    def is_valid(self, data):
        self.can_enroll_in_raffle()

        self.check_user_constraints()

        self.check_user_owns_wallet(data.get("user_wallet_address"))

        self.check_prizetap_winning_chance(
            int(data.get("prizetap_winning_chance_number", 0))
        )


class SetRaffleEntryTxValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs["user_profile"]
        self.raffle_entry: RaffleEntry = kwargs["raffle_entry"]

    def is_owner_of_raffle_entry(self):
        if not self.raffle_entry.user_profile == self.user_profile:
            raise PermissionDenied(
                "You don't have permission to update this raffle entry"
            )

    def is_tx_empty(self):
        if self.raffle_entry.tx_hash:
            raise PermissionDenied("This raffle entry is already updated")

    def is_valid(self, data):
        self.is_owner_of_raffle_entry()
        self.is_tx_empty()

        tx_hash = data.get("tx_hash", None)
        if not tx_hash or len(tx_hash) != 66:
            raise PermissionDenied("Tx hash is not valid")


class SetClaimingPrizeTxValidator:
    def __init__(self, *args, **kwargs):
        self.raffle_entry: RaffleEntry = kwargs["raffle_entry"]

    def is_winner(self):
        if not self.raffle_entry.is_winner:
            raise PermissionDenied("You are not the raffle winner")

    def is_tx_empty(self):
        if self.raffle_entry.claiming_prize_tx:
            raise PermissionDenied("The tx_hash is already set")

    def is_valid(self, data):
        self.is_winner()
        self.is_tx_empty()

        tx_hash = data.get("tx_hash", None)
        if not tx_hash or len(tx_hash) != 66:
            raise PermissionDenied("Tx hash is not valid")


class SetRaffleTxValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs["user_profile"]
        self.raffle: Raffle = kwargs["raffle"]

    def is_owner_of_raffle(self):
        if not self.raffle.creator_profile == self.user_profile:
            raise PermissionDenied("You don't have permission to update this raffle")

    def is_tx_empty(self):
        if self.raffle.tx_hash:
            raise PermissionDenied("This raffle is already updated")

    def is_valid(self, data):
        self.is_owner_of_raffle()
        self.is_tx_empty()

        tx_hash = data.get("tx_hash", None)
        if not tx_hash or len(tx_hash) != 66:
            raise PermissionDenied("Tx hash is not valid")
