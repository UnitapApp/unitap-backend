from datetime import datetime

from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.thirdpartyapp import ZoraUtil


class DidMintZoraNFT(ConstraintVerification):
    app_name = ConstraintApp.ZORA.value
    _param_keys = [ConstraintParam.ADDRESS]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        zora_util = ZoraUtil()
        user_addresses = self.user_addresses
        nft_address = self.param_values[ConstraintParam.ADDRESS.name]
        for address in user_addresses:
            res = zora_util.get_tx(nft_address=nft_address, address=address)
            if res is None:
                continue
            for tx in res.values:
                if (
                    tx.get("method") == "mint"
                    and datetime.strptime(tx.get("timestamp"), "%Y-%m-%dT%H:%M:%S.%fZ")
                    > self.obj.start_at
                ):
                    return True
        return False
