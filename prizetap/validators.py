import json

from rest_framework.exceptions import PermissionDenied

from authentication.models import UserProfile
from core.constraints import ConstraintVerification, get_constraint

from .models import Raffle, RaffleEntry


class RaffleEnrollmentValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs["user_profile"]
        self.raffle: Raffle = kwargs["raffle"]

    def can_enroll_in_raffle(self):
        if not self.raffle.is_claimable:
            raise PermissionDenied("Can't enroll in this raffle")

    def check_user_constraints(self):
        try:
            param_values = json.loads(self.raffle.constraint_params)
        except Exception:
            param_values = {}
        reversed_constraints = self.raffle.reversed_constraints.split(",") if self.raffle.reversed_constraints else []
        for c in self.raffle.constraints.all():
            constraint: ConstraintVerification = get_constraint(c.name)(self.user_profile)
            constraint.response = c.response
            try:
                constraint.param_values = param_values[c.name]
            except KeyError:
                pass
            if str(c.pk) in reversed_constraints:
                if constraint.is_observed():
                    raise PermissionDenied(constraint.response)
            else:
                if not constraint.is_observed():
                    raise PermissionDenied(constraint.response)

    def check_user_wallet_address_is_registered_wallet_for_user(self, user_wallet_address):
        if not self.user_profile.wallets.filter(address=user_wallet_address).exists():
            raise PermissionDenied("This wallet is not registered for this user")

    def is_valid(self, data):
        self.can_enroll_in_raffle()

        self.check_user_constraints()

        self.check_user_wallet_address_is_registered_wallet_for_user(data.get("user_wallet_address"))


class SetRaffleEntryTxValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs["user_profile"]
        self.raffle_entry: RaffleEntry = kwargs["raffle_entry"]

    def is_owner_of_raffle_entry(self):
        if not self.raffle_entry.user_profile == self.user_profile:
            raise PermissionDenied("You don't have permission to update this raffle entry")

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
