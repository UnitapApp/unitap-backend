from authentication.models import UserProfile
from core.constraints import ConstraintParam, ConstraintVerification
from core.models import Chain
from core.utils import NFTClient


class HaveUnitapPass(ConstraintVerification):
    _param_keys = [
        ConstraintParam.MINIMUM,
    ]

    def __init__(self, user_profile: UserProfile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        min_balance = self.param_values[ConstraintParam.MINIMUM.name]
        chain = Chain.objects.get(chain_id=8453)
        nft_client = NFTClient(chain, "0xA27b7B65b0de0c08b002E6be828731FA865027bB")

        user_addresses = [
            nft_client.to_checksum_address(wallet.address.lower())
            for wallet in self.user_profile.wallets.filter(wallet_type=chain.chain_type)
        ]

        user_balance = sum(
            int(nft_client.get_number_of_tokens(user_address))
            for user_address in user_addresses
        )

        if user_balance >= min_balance:
            return True
        return False


class NotHaveUnitapPass(HaveUnitapPass):
    def __init__(self, user_profile: UserProfile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        return not super().is_observed()
