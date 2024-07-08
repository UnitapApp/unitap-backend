from typing import Optional

from core.utils import Web3Utils


class ArbitrumUtils:
    ETH_W3 = Web3Utils("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID")
    ARB_W3 = Web3Utils("https://arb1.arbitrum.io/rpc")
    NOVA_W3 = Web3Utils("https://nova.arbitrum.io/rpc")

    BRIDGE_ADDRESSES = {
        "ethereum": "0x8315177aB297bA92A06054cE80a67Ed4DBd7ed3a",
        "arbitrum": "0x0000000000000000000000000000000000000064",
        "nova": "0x0000000000000000000000000000000000000064",
    }

    BRIDGE_ABI = [
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "l1Token", "type": "address"},
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "amount", "type": "uint256"},
            ],
            "name": "ERC20DepositInitiated",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "amount", "type": "uint256"},
            ],
            "name": "DepositInitiated",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "l1Token", "type": "address"},
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "amount", "type": "uint256"},
            ],
            "name": "WithdrawalInitiated",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "amount", "type": "uint256"},
            ],
            "name": "ETHWithdrawalInitiated",
            "type": "event",
        },
    ]

    def __init__(self):
        self.contracts = {
            "ethereum": self.ETH_W3.set_contract(
                self.BRIDGE_ADDRESSES["ethereum"], self.BRIDGE_ABI
            ),
            "arbitrum": self.ARB_W3.set_contract(
                self.BRIDGE_ADDRESSES["arbitrum"], self.BRIDGE_ABI
            ),
            "nova": self.NOVA_W3.set_contract(
                self.BRIDGE_ADDRESSES["nova"], self.BRIDGE_ABI
            ),
        }

    def check_bridge_transactions(
        self,
        wallet_address: str,
        token_address: Optional[str],
        amount: float,
        source_chain: str,
        target_chain: str,
    ) -> bool:
        if source_chain not in self.contracts or target_chain not in self.contracts:
            raise ValueError(f"Invalid chain: {source_chain} or {target_chain}")

        contract = self.contracts[source_chain]

        if token_address is None:  # ETH transaction
            if source_chain == "ethereum":
                event_name = "DepositInitiated"
            else:
                event_name = "ETHWithdrawalInitiated"

            event = getattr(contract.events, event_name)
            event_filter = event.createFilter(
                fromBlock=0, argument_filters={"from": wallet_address}
            )
        else:  # ERC-20 transaction
            if source_chain == "ethereum":
                event_name = "ERC20DepositInitiated"
            else:
                event_name = "WithdrawalInitiated"

            event = getattr(contract.events, event_name)
            event_filter = event.createFilter(
                fromBlock=0,
                argument_filters={"from": wallet_address, "l1Token": token_address},
            )

        events = event_filter.get_all_entries()
        return any(event["args"]["amount"] >= amount for event in events)

    def check_all_bridge_transactions(
        self, wallet_address: str, token_address: Optional[str], amount: float
    ) -> dict[str, bool]:
        results = {}
        chains = ["ethereum", "arbitrum", "nova"]

        for source in chains:
            for target in chains:
                if source != target:
                    key = f"{source.capitalize()} to {target.capitalize()}"
                    results[key] = self.check_bridge_transactions(
                        wallet_address, token_address, amount, source, target
                    )

        return results
