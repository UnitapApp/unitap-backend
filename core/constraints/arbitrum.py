from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.thirdpartyapp.arbitrum import ArbitrumUtils


class HasBridgedToken(ConstraintVerification):
    _param_keys = [
        ConstraintParam.ADDRESS,
        ConstraintParam.MINIMUM,
        ConstraintParam.CHAIN,
    ]
    app_name = ConstraintApp.ARBITRUM.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        minimum_amount = float(self.param_values[ConstraintParam.MINIMUM.name])
        chain = self.param_values[ConstraintParam.CHAIN.name]
        token_address = self.param_values[ConstraintParam.ADDRESS.name]

        arb_utils = ArbitrumUtils()
        user_wallets = self.user_addresses

        for wallet in user_wallets:
            bridging_results = arb_utils.check_bridge_transactions(
                wallet, token_address, minimum_amount
            )

        if chain == "ethereum_to_arbitrum":
            return bridging_results["Ethereum to Arbitrum"]
        elif chain == "arbitrum_to_ethereum":
            return bridging_results["Arbitrum to Ethereum"]
        elif chain == "arbitrum_to_nova":
            return bridging_results["Arbitrum to Nova"]
        elif chain == "nova_to_arbitrum":
            return bridging_results["Nova to Arbitrum"]
        elif chain == "any":
            return any(bridging_results.values())
        else:
            raise ValueError(f"Invalid chain parameter: {chain}")
