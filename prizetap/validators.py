from .models import RaffleEntry
from faucet.faucet_manager.credit_strategy import WeeklyCreditStrategy
from faucet.models import GlobalSettings

def has_weekly_credit_left(user_profile):
    return (
        RaffleEntry.objects.filter(
            user_profile=user_profile,
            created_at__gte=WeeklyCreditStrategy.get_last_monday(),
        ).count()
        < GlobalSettings.objects.first().prizetap_weekly_claim_limit
    )