from authentication.models import UserProfile
from core.constraints import ConstraintVerification
from core.models import Chain

from .utils import UnitapPassClient


class HaveUnitapPass(ConstraintVerification):
    def __init__(self, user_profile: UserProfile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        chain = Chain.objects.get(chain_id=1)
        self.unitappass_client = UnitapPassClient(chain)

        user_addresses = [
            self.unitappass_client.w3.to_checksum_address(wallet.address.lower())
            for wallet in self.user_profile.wallets.filter(wallet_type=chain.chain_type)
        ]

        for user_address in user_addresses:
            if self.unitappass_client.is_holder(user_address):
                return True
        return False


class NotHaveUnitapPass(HaveUnitapPass):
    def __init__(self, user_profile: UserProfile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        return not super().is_observed()
