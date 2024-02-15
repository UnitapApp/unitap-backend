from rest_framework.exceptions import PermissionDenied
from authentication.models import UserProfile
from .models import TokenDistribution


class SetDistributionTxValidator:
    def __init__(self, *args, **kwargs):
        self.user_profile: UserProfile = kwargs["user_profile"]
        self.token_distribution: TokenDistribution = kwargs["token_distribution"]

    def is_owner_of_raffle(self):
        if not self.token_distribution.distributor_profile == self.user_profile:
            raise PermissionDenied(
                "You don't have permission to update this token_distribution")

    def is_tx_empty(self):
        if self.token_distribution.tx_hash:
            raise PermissionDenied("This token_distribution is already updated")

    def is_valid(self, data):
        self.is_owner_of_raffle()
        self.is_tx_empty()

        tx_hash = data.get("tx_hash", None)
        if not tx_hash or len(tx_hash) != 66:
            raise PermissionDenied("Tx hash is not valid")
