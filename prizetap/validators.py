import json
from .models import RaffleEntry
from faucet.faucet_manager.credit_strategy import WeeklyCreditStrategy
from faucet.models import GlobalSettings
from rest_framework.exceptions import PermissionDenied
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
        
    def check_user_constraints(self):
        try:
            param_values = json.loads(self.raffle.constraint_params)
        except:
            param_values = {}
        for c in self.raffle.constraints.all():
            constraint: ConstraintVerification = eval(c.name)(self.user_profile)
            try:
                constraint.set_param_values(param_values[c.name])
            except KeyError:
                pass
            if not constraint.is_observed(self.raffle.constraint_params):
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

        self.check_user_constraints()

        self.check_user_has_wallet()


class ClaimPrizeValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs['user_profile']
        self.raffle: Raffle = kwargs['raffle']

    def can_claim_prize(self):
        if not self.raffle.is_expired:
            raise PermissionDenied(
                "The raffle is not over"
            )
        if not self.raffle.winner or self.raffle.winner != self.user_profile:
            raise PermissionDenied(
                "You are not the raffle winner"
            )
            
    def is_valid(self, data):
        self.can_claim_prize()

    

class SetRaffleEntryTxValidator:
    
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs['user_profile']
        self.raffle_entry: RaffleEntry = kwargs['raffle_entry']

    def is_owner_of_raffle_entry(self):
        if not self.raffle_entry.user_profile == self.user_profile:
            raise PermissionDenied(
                "You don't have permission to update this raffle entry"
            )
        
    def is_tx_empty(self):
        if self.raffle_entry.tx_hash:
            raise PermissionDenied(
                "This raffle entry is already updated"
            )

    def is_valid(self, data):
        self.is_owner_of_raffle_entry()
        self.is_tx_empty()

        tx_hash = data.get("tx_hash", None)
        if not tx_hash or len(tx_hash) != 66:
            raise PermissionDenied(
                "Tx hash is not valid"
            )

class SetClaimingPrizeTxValidator:
    
    def __init__(self, *args, **kwargs):
        self.raffle_entry: RaffleEntry = kwargs['raffle_entry']
        
    def is_winner(self):
        if not self.raffle_entry.is_winner:
            raise PermissionDenied(
                "You are not the raffle winner"
            )
        
    def is_tx_empty(self):
        if self.raffle_entry.claiming_prize_tx:
            raise PermissionDenied(
                "The tx_hash is already set"
            )

    def is_valid(self, data):
        self.is_winner()
        self.is_tx_empty()

        tx_hash = data.get("tx_hash", None)
        if not tx_hash or len(tx_hash) != 66:
            raise PermissionDenied(
                "Tx hash is not valid"
            )

