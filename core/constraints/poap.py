from core.constraints.abstract import ConstraintApp, ConstraintVerification
from core.thirdpartyapp import ENSUtil


class HasPOAPVerification(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.POAP.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import NetworkTypes

        user_wallets = self.user_profile.wallets.filter(wallet_type=NetworkTypes.EVM)
        ens_util = ENSUtil()
        for wallet in user_wallets:
            if ens_util.get_name(wallet.address) is not None:
                return True
        return False
