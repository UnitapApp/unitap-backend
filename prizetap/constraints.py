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
        user_address: str = self.user_profile.wallets.get(wallet_type=chain.chain_type).address
        user_address = self.unitappass_client.to_checksum_address(user_address.lower())
        return self.unitappass_client.is_holder(user_address)


class NotHaveUnitapPass(HaveUnitapPass):
    def __init__(self, user_profile: UserProfile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        return not super().is_observed()
