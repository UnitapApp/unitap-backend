manager_abi = [
    {
        "type": "constructor",
        "stateMutability": "nonpayable",
        "inputs": [
            {"type": "uint256", "name": "period_", "internalType": "uint256"},
            {"type": "uint256", "name": "periodicMaxCap_", "internalType": "uint256"},
            {"type": "address", "name": "admin", "internalType": "address"},
            {"type": "address", "name": "unitap", "internalType": "address"},
        ],
    },
    {
        "type": "event",
        "name": "RoleAdminChanged",
        "inputs": [
            {
                "type": "bytes32",
                "name": "role",
                "internalType": "bytes32",
                "indexed": True,
            },
            {
                "type": "bytes32",
                "name": "previousAdminRole",
                "internalType": "bytes32",
                "indexed": True,
            },
            {
                "type": "bytes32",
                "name": "newAdminRole",
                "internalType": "bytes32",
                "indexed": True,
            },
        ],
        "anonymous": False,
    },
    {
        "type": "event",
        "name": "RoleGranted",
        "inputs": [
            {
                "type": "bytes32",
                "name": "role",
                "internalType": "bytes32",
                "indexed": True,
            },
            {
                "type": "address",
                "name": "account",
                "internalType": "address",
                "indexed": True,
            },
            {
                "type": "address",
                "name": "sender",
                "internalType": "address",
                "indexed": True,
            },
        ],
        "anonymous": False,
    },
    {
        "type": "event",
        "name": "RoleRevoked",
        "inputs": [
            {
                "type": "bytes32",
                "name": "role",
                "internalType": "bytes32",
                "indexed": True,
            },
            {
                "type": "address",
                "name": "account",
                "internalType": "address",
                "indexed": True,
            },
            {
                "type": "address",
                "name": "sender",
                "internalType": "address",
                "indexed": True,
            },
        ],
        "anonymous": False,
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "bytes32", "name": "", "internalType": "bytes32"}],
        "name": "DEFAULT_ADMIN_ROLE",
        "inputs": [],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "bytes32", "name": "", "internalType": "bytes32"}],
        "name": "UNITAP_ROLE",
        "inputs": [],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
        "name": "erc20PeriodicMaxCap",
        "inputs": [{"type": "address", "name": "", "internalType": "address"}],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
        "name": "erc20Periods",
        "inputs": [{"type": "address", "name": "", "internalType": "address"}],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
        "name": "erc20Withdrawals",
        "inputs": [
            {"type": "address", "name": "", "internalType": "address"},
            {"type": "uint256", "name": "", "internalType": "uint256"},
        ],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
        "name": "ethPeriod",
        "inputs": [],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
        "name": "ethPeriodicMaxCap",
        "inputs": [],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
        "name": "ethTotalWithdrawals",
        "inputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
        "name": "getActivePeriod",
        "inputs": [{"type": "uint256", "name": "period_", "internalType": "uint256"}],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "bytes32", "name": "", "internalType": "bytes32"}],
        "name": "getRoleAdmin",
        "inputs": [{"type": "bytes32", "name": "role", "internalType": "bytes32"}],
    },
    {
        "type": "function",
        "stateMutability": "nonpayable",
        "outputs": [],
        "name": "grantRole",
        "inputs": [
            {"type": "bytes32", "name": "role", "internalType": "bytes32"},
            {"type": "address", "name": "account", "internalType": "address"},
        ],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "bool", "name": "", "internalType": "bool"}],
        "name": "hasRole",
        "inputs": [
            {"type": "bytes32", "name": "role", "internalType": "bytes32"},
            {"type": "address", "name": "account", "internalType": "address"},
        ],
    },
    {
        "type": "function",
        "stateMutability": "nonpayable",
        "outputs": [],
        "name": "multiWithdrawErc20",
        "inputs": [
            {
                "type": "tuple[]",
                "name": "recipients",
                "internalType": "struct Erc20Recipient[]",
                "components": [
                    {"type": "address", "name": "token", "internalType": "address"},
                    {"type": "address", "name": "to", "internalType": "address"},
                    {"type": "uint256", "name": "amount", "internalType": "uint256"},
                ],
            }
        ],
    },
    {
        "type": "function",
        "stateMutability": "nonpayable",
        "outputs": [],
        "name": "multiWithdrawEth",
        "inputs": [
            {
                "type": "tuple[]",
                "name": "recipients",
                "internalType": "struct EthRecipient[]",
                "components": [
                    {"type": "address", "name": "to", "internalType": "address"},
                    {"type": "uint256", "name": "amount", "internalType": "uint256"},
                ],
            }
        ],
    },
    {
        "type": "function",
        "stateMutability": "nonpayable",
        "outputs": [],
        "name": "renounceRole",
        "inputs": [
            {"type": "bytes32", "name": "role", "internalType": "bytes32"},
            {"type": "address", "name": "account", "internalType": "address"},
        ],
    },
    {
        "type": "function",
        "stateMutability": "nonpayable",
        "outputs": [],
        "name": "revokeRole",
        "inputs": [
            {"type": "bytes32", "name": "role", "internalType": "bytes32"},
            {"type": "address", "name": "account", "internalType": "address"},
        ],
    },
    {
        "type": "function",
        "stateMutability": "nonpayable",
        "outputs": [],
        "name": "setErc20Params",
        "inputs": [
            {"type": "address", "name": "token", "internalType": "address"},
            {"type": "uint256", "name": "period_", "internalType": "uint256"},
            {"type": "uint256", "name": "periodicMaxCap_", "internalType": "uint256"},
        ],
    },
    {
        "type": "function",
        "stateMutability": "nonpayable",
        "outputs": [],
        "name": "setEthParams",
        "inputs": [
            {"type": "uint256", "name": "period_", "internalType": "uint256"},
            {"type": "uint256", "name": "periodicMaxCap_", "internalType": "uint256"},
        ],
    },
    {
        "type": "function",
        "stateMutability": "view",
        "outputs": [{"type": "bool", "name": "", "internalType": "bool"}],
        "name": "supportsInterface",
        "inputs": [{"type": "bytes4", "name": "interfaceId", "internalType": "bytes4"}],
    },
    {
        "type": "function",
        "stateMutability": "nonpayable",
        "outputs": [],
        "name": "withdrawErc20",
        "inputs": [
            {"type": "address", "name": "token", "internalType": "address"},
            {"type": "uint256", "name": "amount", "internalType": "uint256"},
            {"type": "address", "name": "to", "internalType": "address"},
        ],
    },
    {
        "type": "function",
        "stateMutability": "nonpayable",
        "outputs": [],
        "name": "withdrawEth",
        "inputs": [
            {"type": "uint256", "name": "amount", "internalType": "uint256"},
            {"type": "address", "name": "to", "internalType": "address"},
        ],
    },
    {"type": "receive", "stateMutability": "payable"},
]
