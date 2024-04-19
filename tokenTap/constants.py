CONTRACT_ADDRESSES = {
    # "80001": "0xd78Bc9369ef4617F5E3965d47838a0FCc4B9145F",
    # "42161": "0x785996054151487B296005aAeC8CAE7C209D1385",
    # "30": "0x785996054151487B296005aAeC8CAE7C209D1385",
}

ERC20_TOKENTAP_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "admin", "type": "address"},
            {"internalType": "uint256", "name": "_muonAppId", "type": "uint256"},
            {
                "components": [
                    {"internalType": "uint256", "name": "x", "type": "uint256"},
                    {"internalType": "uint8", "name": "parity", "type": "uint8"},
                ],
                "internalType": "struct IMuonClient.PublicKey",
                "name": "_muonPublicKey",
                "type": "tuple",
            },
            {"internalType": "address", "name": "_muon", "type": "address"},
            {"internalType": "address", "name": "_muonValidGateway", "type": "address"},
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "recipient",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "distributionId",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256",
            },
        ],
        "name": "DistributionRefunded",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "role",
                "type": "bytes32",
            },
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "previousAdminRole",
                "type": "bytes32",
            },
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "newAdminRole",
                "type": "bytes32",
            },
        ],
        "name": "RoleAdminChanged",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "role",
                "type": "bytes32",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "account",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "sender",
                "type": "address",
            },
        ],
        "name": "RoleGranted",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "role",
                "type": "bytes32",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "account",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "sender",
                "type": "address",
            },
        ],
        "name": "RoleRevoked",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "distributionId",
                "type": "uint256",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "provider",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "token",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "maxNumClaims",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "claimAmount",
                "type": "uint256",
            },
        ],
        "name": "TokenDistributed",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "token",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "claimId",
                "type": "uint256",
            },
        ],
        "name": "TokensClaimed",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "DAO_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "DEFAULT_ADMIN_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "user", "type": "address"},
            {"internalType": "uint256", "name": "distributionId", "type": "uint256"},
            {"internalType": "uint256", "name": "claimId", "type": "uint256"},
            {"internalType": "bytes", "name": "reqId", "type": "bytes"},
            {
                "components": [
                    {"internalType": "uint256", "name": "signature", "type": "uint256"},
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "address", "name": "nonce", "type": "address"},
                ],
                "internalType": "struct IMuonClient.SchnorrSign",
                "name": "signature",
                "type": "tuple",
            },
            {"internalType": "bytes", "name": "gatewaySignature", "type": "bytes"},
        ],
        "name": "claimToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "maxNumClaims", "type": "uint256"},
            {"internalType": "uint256", "name": "claimAmount", "type": "uint256"},
            {"internalType": "uint256", "name": "startTime", "type": "uint256"},
            {"internalType": "uint256", "name": "endTime", "type": "uint256"},
        ],
        "name": "distributeToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "distributions",
        "outputs": [
            {"internalType": "address", "name": "provider", "type": "address"},
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "maxNumClaims", "type": "uint256"},
            {"internalType": "uint256", "name": "claimAmount", "type": "uint256"},
            {"internalType": "uint256", "name": "claimsCount", "type": "uint256"},
            {"internalType": "uint256", "name": "startTime", "type": "uint256"},
            {"internalType": "uint256", "name": "endTime", "type": "uint256"},
            {"internalType": "bool", "name": "isRefunded", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"}],
        "name": "getRoleAdmin",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "role", "type": "bytes32"},
            {"internalType": "address", "name": "account", "type": "address"},
        ],
        "name": "grantRole",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "role", "type": "bytes32"},
            {"internalType": "address", "name": "account", "type": "address"},
        ],
        "name": "hasRole",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "lastDistributionId",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "muon",
        "outputs": [
            {"internalType": "contract IMuonClient", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "muonAppId",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "muonPublicKey",
        "outputs": [
            {"internalType": "uint256", "name": "x", "type": "uint256"},
            {"internalType": "uint8", "name": "parity", "type": "uint8"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "muonValidGateway",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "role", "type": "bytes32"},
            {"internalType": "address", "name": "account", "type": "address"},
        ],
        "name": "renounceRole",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "role", "type": "bytes32"},
            {"internalType": "address", "name": "account", "type": "address"},
        ],
        "name": "revokeRole",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_muonAddress", "type": "address"}
        ],
        "name": "setMuonAddress",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_muonAppId", "type": "uint256"}
        ],
        "name": "setMuonAppId",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_gatewayAddress", "type": "address"}
        ],
        "name": "setMuonGateway",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "x", "type": "uint256"},
                    {"internalType": "uint8", "name": "parity", "type": "uint8"},
                ],
                "internalType": "struct IMuonClient.PublicKey",
                "name": "_muonPublicKey",
                "type": "tuple",
            }
        ],
        "name": "setMuonPublicKey",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes4", "name": "interfaceId", "type": "bytes4"}],
        "name": "supportsInterface",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "usedClaims",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "distributionId", "type": "uint256"},
        ],
        "name": "withdrawReaminingTokens",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]
