import json

from rest_framework.exceptions import PermissionDenied, ValidationError

from authentication.models import UserProfile
from core.constraints import ConstraintVerification, get_constraint

from .models import Raffle, RaffleEntry


class RaffleEnrollmentValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs["user_profile"]
        self.raffle: Raffle = kwargs["raffle"]
        self.raffle_data: dict = (
            kwargs["raffle_data"] if "raffle_data" in kwargs else None
        )

    def can_enroll_in_raffle(self):
        if not self.raffle.is_claimable:
            raise PermissionDenied("Can't enroll in this raffle")

    def check_user_constraints(self):
        try:
            param_values = json.loads(self.raffle.constraint_params)
        except Exception:
            param_values = {}
        for c in self.raffle.constraints.all():
            constraint: ConstraintVerification = get_constraint(c.name)(
                self.user_profile
            )
            constraint.response = c.response
            try:
                constraint.param_values = param_values[c.name]
            except KeyError:
                pass
            if str(c.pk) in self.raffle.reversed_constraints_list:
                if self.raffle_data and str(c.pk) in self.raffle_data.keys():
                    cdata = (
                        dict(self.raffle_data[str(c.pk)])
                        if self.raffle_data
                        else dict()
                    )
                    if constraint.is_observed(
                        **cdata, from_time=int(self.raffle.start_at.timestamp())
                    ):
                        raise PermissionDenied(constraint.response)
                elif constraint.is_observed(
                    from_time=int(self.raffle.start_at.timestamp())
                ):
                    raise PermissionDenied(constraint.response)
            else:
                if self.raffle_data and str(c.pk) in self.raffle_data.keys():
                    cdata = (
                        dict(self.raffle_data[str(c.pk)])
                        if self.raffle_data
                        else dict()
                    )
                    if not constraint.is_observed(
                        **cdata, from_time=int(self.raffle.start_at.timestamp())
                    ):
                        raise PermissionDenied(constraint.response)
                elif not constraint.is_observed(
                    from_time=int(self.raffle.start_at.timestamp())
                ):
                    raise PermissionDenied(constraint.response)

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
