from authentication.models import UserProfile
from core.constraints import ConstraintVerification
from core.models import Chain
from core.utils import NFTClient


class HaveUnitapPass(ConstraintVerification):
    def __init__(self, user_profile: UserProfile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        chain = Chain.objects.get(chain_id=1)
        nft_client = NFTClient(chain, "0x23826Fd930916718a98A21FF170088FBb4C30803")

        user_addresses = [
            nft_client.to_checksum_address(wallet.address.lower())
            for wallet in self.user_profile.wallets.filter(wallet_type=chain.chain_type)
        ]

        for user_address in user_addresses:
            if nft_client.get_number_of_tokens(user_address) > 0:
                return True
        return False


class NotHaveUnitapPass(HaveUnitapPass):
    def __init__(self, user_profile: UserProfile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        return not super().is_observed()
