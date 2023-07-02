from .models import RaffleEntry
from faucet.faucet_manager.credit_strategy import WeeklyCreditStrategy
from faucet.models import GlobalSettings
from django.core.exceptions import ValidationError
from authentication.models import UserProfile
from .models import RaffleEntry

def has_weekly_credit_left(user_profile):
    return (
        RaffleEntry.objects.filter(
            user_profile=user_profile,
            created_at__gte=WeeklyCreditStrategy.get_last_monday(),
        ).count()
        < GlobalSettings.objects.first().prizetap_weekly_claim_limit
    )

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

