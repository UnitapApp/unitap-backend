from web3 import Web3


class ArbitrumUtils:
    def __init__(self):
        # Initialize Web3 instances
        self.eth_w3 = Web3.HTTPProvider(
            "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
        )
        self.arb_w3 = Web3.HTTPProvider("https://arb1.arbitrum.io/rpc")
        self.nova_w3 = Web3.HTTPProvider("https://nova.arbitrum.io/rpc")

        # Bridge contract addresses
        self.eth_arb_bridge = "0x8315177aB297bA92A06054cE80a67Ed4DBd7ed3a"
        self.arb_eth_bridge = "0x0000000000000000000000000000000000000064"
        self.arb_nova_bridge = "0x0000000000000000000000000000000000000064"
        self.nova_arb_bridge = "0x0000000000000000000000000000000000000064"

        # ABI for the bridge contracts
        self.bridge_abi = [
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
                    {"indexed": True, "name": "l1Token", "type": "address"},
                    {"indexed": True, "name": "from", "type": "address"},
                    {"indexed": True, "name": "to", "type": "address"},
                    {"indexed": False, "name": "amount", "type": "uint256"},
                ],
                "name": "WithdrawalInitiated",
                "type": "event",
            },
        ]

    def check_bridge_transactions(self, wallet_address, token_address, amount):
        # Create contract instances
        eth_arb_contract = self.eth_w3.eth.contract(
            address=self.eth_arb_bridge, abi=self.bridge_abi
        )
        arb_eth_contract = self.arb_w3.eth.contract(
            address=self.arb_eth_bridge, abi=self.bridge_abi
        )
        arb_nova_contract = self.arb_w3.eth.contract(
            address=self.arb_nova_bridge, abi=self.bridge_abi
        )
        nova_arb_contract = self.nova_w3.eth.contract(
            address=self.nova_arb_bridge, abi=self.bridge_abi
        )

        results = {}

        # Check Ethereum to Arbitrum
        eth_arb_filter = eth_arb_contract.events.ERC20DepositInitiated.createFilter(
            fromBlock=0,
            argument_filters={"from": wallet_address, "l1Token": token_address},
        )
        eth_arb_events = eth_arb_filter.get_all_entries()
        results["Ethereum to Arbitrum"] = any(
            event["args"]["amount"] >= amount for event in eth_arb_events
        )

        # Check Arbitrum to Ethereum
        arb_eth_filter = arb_eth_contract.events.WithdrawalInitiated.createFilter(
            fromBlock=0,
            argument_filters={"from": wallet_address, "l1Token": token_address},
        )
        arb_eth_events = arb_eth_filter.get_all_entries()
        results["Arbitrum to Ethereum"] = any(
            event["args"]["amount"] >= amount for event in arb_eth_events
        )

        # Check Arbitrum to Nova
        arb_nova_filter = arb_nova_contract.events.WithdrawalInitiated.createFilter(
            fromBlock=0,
            argument_filters={"from": wallet_address, "l1Token": token_address},
        )
        arb_nova_events = arb_nova_filter.get_all_entries()
        results["Arbitrum to Nova"] = any(
            event["args"]["amount"] >= amount for event in arb_nova_events
        )

        # Check Nova to Arbitrum
        nova_arb_filter = nova_arb_contract.events.WithdrawalInitiated.createFilter(
            fromBlock=0,
            argument_filters={"from": wallet_address, "l1Token": token_address},
        )
        nova_arb_events = nova_arb_filter.get_all_entries()
        results["Nova to Arbitrum"] = any(
            event["args"]["amount"] >= amount for event in nova_arb_events
        )

        return results
