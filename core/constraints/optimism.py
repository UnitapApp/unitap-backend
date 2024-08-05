import logging

from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.utils import InvalidAddressException, TokenClient


class DidDelegateOPToAddress(ConstraintVerification):
    app_name = ConstraintApp.OPTIMISM.value
    _param_keys = (
        ConstraintParam.MINIMUM,
        ConstraintParam.ADDRESS,
    )

    OPTIMISM_CHAIN_ID = "10"
    OP_TOKEN_ABI = [
        {
            "inputs": [
                {"internalType": "address", "name": "account", "type": "address"}
            ],
            "name": "delegates",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "account", "type": "address"}
            ],
            "name": "balanceOf",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]
    OP_TOKEN_CONTRACT = "0x4200000000000000000000000000000000000042"

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import Chain

        try:
            chain = Chain.objects.get(chain_id=self.OPTIMISM_CHAIN_ID)
        except Chain.DoesNotExist:
            logging.warning("Optimism chain not found")
            return False
        token_client = TokenClient(
            chain=chain, contract=self.OP_TOKEN_CONTRACT, abi=self.OP_TOKEN_ABI
        )
        delegated_power = 0
        for user_address in self.user_addresses:
            try:
                address = token_client.to_checksum_address(user_address)
                delegated_address = token_client.get_delegates_address()
                if (
                    delegated_address.lower()
                    != self.param_values[ConstraintParam.ADDRESS.name].lower()
                ):
                    continue
                balance = token_client.get_non_native_token_balance(address)
                delegated_power += balance
            except InvalidAddressException:
                pass
        if delegated_power >= int(self.param_values[ConstraintParam.MINIMUM.name]):
            return True
        return False
