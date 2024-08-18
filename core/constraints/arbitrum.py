import logging

from django.db.models.functions import Lower

from core.constraints.abstract import (
    ConstraintApp,
    ConstraintParam,
    ConstraintVerification,
)
from core.thirdpartyapp import Subgraph
from core.utils import InvalidAddressException, TokenClient, Web3Utils


class BridgeEthToArb(ConstraintVerification):
    app_name = ConstraintApp.ARBITRUM.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        try:
            return self.has_bridged(
                kwargs["from_time"] if "from_time" in kwargs else None
            )
        except Exception as e:
            print(e)
        return False

    def has_bridged(self, from_time=None):
        subgraph = Subgraph()

        user_wallets = self.user_profile.wallets.values_list(
            Lower("address"), flat=True
        )

        if from_time:
            query = """
            query GetMessageDelivereds($wallets: [String], $fromTime: String) {
                messageDelivereds(
                    where: {
                        txOrigin_in: $wallets
                        kind: 12
                        timestamp_gt: $fromTime
                    }
                ) {
                    id
                    transactionHash
                }
            }
            """
            vars = {"wallets": list(user_wallets), "fromTime": str(from_time)}
        else:
            query = """
            query GetMessageDelivereds($wallets: [String]) {
                messageDelivereds(
                    where: {
                        txOrigin_in: $wallets
                        kind: 12
                    }
                ) {
                    id
                    transactionHash
                }
            }
            """
            vars = {
                "wallets": list(user_wallets),
            }

        res = subgraph.send_post_request(
            subgraph.path.get("arb_bridge_mainnet"), query=query, vars=vars
        )
        match res:
            case None:
                return False
            case {"data": {"messageDelivereds": messages}} if len(messages) > 0:
                return True
            case _:
                return False


class DelegateArb(ConstraintVerification):
    app_name = ConstraintApp.ARBITRUM.value

    _param_keys = []

    ARBITRUM_CHAIN_ID = "42161"
    ARB_TOKEN_ABI = [
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
    ARB_TOKEN_CONTRACT = "0x912CE59144191C1204E64559FE8253a0e49E6548"

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from core.models import Chain

        try:
            chain = Chain.objects.get(chain_id=self.ARBITRUM_CHAIN_ID)
        except Chain.DoesNotExist:
            logging.warning("Arbitrum chain not found")
            return False
        token_client = TokenClient(
            chain=chain, contract=self.ARB_TOKEN_CONTRACT, abi=self.ARB_TOKEN_ABI
        )
        delegated_power = 0
        for user_address in self.user_addresses:
            try:
                address = token_client.to_checksum_address(user_address)
                delegated_address = token_client.get_delegates_address()
                if not self.param_keys():
                    if delegated_address.lower() != Web3Utils.ZERO_ADDRESS:
                        return True
                elif (
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


class DidDelegateArbToAddress(DelegateArb):
    _param_keys = (
        ConstraintParam.ADDRESS,
        ConstraintParam.MINIMUM,
    )

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)
