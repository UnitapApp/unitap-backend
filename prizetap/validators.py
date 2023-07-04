from .models import RaffleEntry
from faucet.faucet_manager.credit_strategy import WeeklyCreditStrategy
from faucet.models import GlobalSettings
from rest_framework.exceptions import ValidationError, PermissionDenied
from authentication.models import NetworkTypes, UserProfile
from .models import RaffleEntry, Raffle
from .constraints import *

def has_weekly_credit_left(user_profile):
    return (
        RaffleEntry.objects.filter(
            user_profile=user_profile,
            created_at__gte=WeeklyCreditStrategy.get_last_monday(),
        ).count()
        < GlobalSettings.objects.first().prizetap_weekly_claim_limit
    )

class RaffleEnrollmentValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs['user_profile']
        self.raffle: Raffle = kwargs['raffle']

    def can_enroll_in_raffle(self):
        if not self.raffle.is_claimable:
            raise PermissionDenied(
                "Can't enroll in this raffle"
            )
        
    def check_user_is_already_enrolled(self):
        if RaffleEntry.objects.filter(
            raffle=self.raffle,
            user_profile=self.user_profile
        ).exists():
            raise PermissionDenied(
                "You're already enrolled in this raffle"
            )
        
    def check_user_constraints(self):
        for c in self.raffle.constraints.all():
            constraint: ConstraintVerification = eval(c.name)(self.user_profile)
            if not constraint.is_observed():
                raise PermissionDenied(
                    constraint.response()
                )

    def check_user_has_wallet(self):
        if not self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM).exists():
            raise PermissionDenied(
                "You have not connected an EVM wallet to your account"
            )

    def is_valid(self, data):
        self.can_enroll_in_raffle()

        self.check_user_is_already_enrolled()

        self.check_user_constraints()

        self.check_user_has_wallet()

    

class SetRaffleEntryTxValidator:
    
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs['user_profile']
        self.raffle_entry: RaffleEntry = kwargs['raffle_entry']

    def is_owner_of_raffle_entry(self):
        if not self.raffle_entry.user_profile == self.user_profile:
            raise ValidationError("You don't have permission to update this raffle entry")
        
    def is_tx_empty(self):
        if self.raffle_entry.tx_hash:
            raise ValidationError("This raffle entry is already updated")

    def is_valid(self, data):
        self.is_owner_of_raffle_entry()
        self.is_tx_empty()

        tx_hash = data.get("tx_hash", None)
        if not tx_hash or len(tx_hash) != 66:
            raise ValidationError("Tx hash is not valid")

