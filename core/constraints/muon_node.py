from django.db.models.functions import Lower

from core.constraints.abstract import ConstraintApp, ConstraintVerification
from core.utils import Web3Utils

MUON_NODE_MANAGER_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "stakerAddress", "type": "address"}
        ],
        "name": "stakerAddressInfo",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint64", "name": "id", "type": "uint64"},
                    {
                        "internalType": "address",
                        "name": "nodeAddress",
                        "type": "address",
                    },
                    {
                        "internalType": "address",
                        "name": "stakerAddress",
                        "type": "address",
                    },
                    {"internalType": "string", "name": "peerId", "type": "string"},
                    {"internalType": "bool", "name": "active", "type": "bool"},
                    {"internalType": "uint8", "name": "tier", "type": "uint8"},
                    {"internalType": "uint64[]", "name": "roles", "type": "uint64[]"},
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "lastEditTime",
                        "type": "uint256",
                    },
                ],
                "internalType": "struct IMuonNodeManager.Node",
                "name": "node",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    }
]


class HasMuonNode(ConstraintVerification):
    app_name = ConstraintApp.MUON.value
    CHAIN_ID = 56
    CONTRACT_ADDR = "0x6eA3096eB0fAf5c1DEb970DCd29A6b10a48DaD83"

    def __init__(self, user_profile) -> None:
        from core.models import Chain

        super().__init__(user_profile)
        self.chain = Chain.objects.get(chain_id=HasMuonNode.CHAIN_ID)
        self.web3_utils = Web3Utils(self.chain.rpc_url_private, self.chain.poa)
        self.web3_utils.set_contract(HasMuonNode.CONTRACT_ADDR, MUON_NODE_MANAGER_ABI)

    def is_observed(self, *args, **kwargs) -> bool:
        try:
            return self.has_node()
        except Exception as e:
            print(e)
        return False

    def has_node(self):
        user_wallets = self.user_profile.wallets.values_list(
            Lower("address"), flat=True
        )

        for wallet in user_wallets:
            func = self.web3_utils.contract.functions.stakerAddressInfo(
                self.web3_utils.to_checksum_address(wallet)
            )
            node = self.web3_utils.contract_call(func)
            if node and node[0] != 0 and node[4]:
                return True

        return False
