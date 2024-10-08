from brightIDfaucet.settings import DEPLOYMENT_ENV

PRIZETAP_ERC20_ABI = [
    {
        "inputs": [
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
            {"internalType": "address", "name": "_admin", "type": "address"},
            {"internalType": "address", "name": "_operator", "type": "address"},
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "multiplier",
                "type": "uint256",
            },
        ],
        "name": "Participate",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "account",
                "type": "address",
            }
        ],
        "name": "Paused",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "winner",
                "type": "address",
            },
        ],
        "name": "PrizeClaimed",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            }
        ],
        "name": "PrizeRefunded",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "initiator",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
        ],
        "name": "RaffleCreated",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "rejector",
                "type": "address",
            },
        ],
        "name": "RaffleRejected",
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
                "internalType": "address",
                "name": "account",
                "type": "address",
            }
        ],
        "name": "Unpaused",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "fromId",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "toId",
                "type": "uint256",
            },
        ],
        "name": "WinnersSpecified",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "DEFAULT_ADMIN_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "MAX_NUM_WINNERS",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "OPERATOR_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_amount", "type": "uint256"},
            {"internalType": "address", "name": "_to", "type": "address"},
            {"internalType": "address", "name": "_tokenAddr", "type": "address"},
        ],
        "name": "adminWithdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "address[]", "name": "participants", "type": "address[]"},
            {"internalType": "uint256[]", "name": "multipliers", "type": "uint256[]"},
        ],
        "name": "batchParticipate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "claimPrize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "address", "name": "currency", "type": "address"},
            {"internalType": "uint256", "name": "maxParticipants", "type": "uint256"},
            {"internalType": "uint256", "name": "maxMultiplier", "type": "uint256"},
            {"internalType": "uint256", "name": "startTime", "type": "uint256"},
            {"internalType": "uint256", "name": "endTime", "type": "uint256"},
            {"internalType": "uint256", "name": "winnersCount", "type": "uint256"},
            {"internalType": "bytes32", "name": "requirementsHash", "type": "bytes32"},
        ],
        "name": "createRaffle",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "fromId", "type": "uint256"},
            {"internalType": "uint256", "name": "toId", "type": "uint256"},
        ],
        "name": "getParticipants",
        "outputs": [
            {"internalType": "address[]", "name": "participants", "type": "address[]"}
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
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "fromId", "type": "uint256"},
            {"internalType": "uint256", "name": "toId", "type": "uint256"},
        ],
        "name": "getWinners",
        "outputs": [
            {"internalType": "address[]", "name": "winners", "type": "address[]"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "getWinnersCount",
        "outputs": [
            {"internalType": "uint256", "name": "winnersCount", "type": "uint256"}
        ],
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
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "name": "isParticipated",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "address", "name": "", "type": "address"},
        ],
        "name": "isWinner",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "address", "name": "", "type": "address"},
        ],
        "name": "isWinnerClaimed",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "lastNotWinnerIndexes",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "lastRaffleId",
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
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "name": "participantPositions",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "multiplier", "type": "uint256"},
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
        "name": "participateInRaffle",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "pause",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "paused",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "name": "raffleParticipants",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "name": "raffleWinners",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "raffles",
        "outputs": [
            {"internalType": "address", "name": "initiator", "type": "address"},
            {"internalType": "uint256", "name": "prizeAmount", "type": "uint256"},
            {"internalType": "address", "name": "currency", "type": "address"},
            {"internalType": "uint256", "name": "maxParticipants", "type": "uint256"},
            {"internalType": "uint256", "name": "maxMultiplier", "type": "uint256"},
            {"internalType": "uint256", "name": "startTime", "type": "uint256"},
            {"internalType": "uint256", "name": "endTime", "type": "uint256"},
            {
                "internalType": "uint256",
                "name": "lastParticipantIndex",
                "type": "uint256",
            },
            {"internalType": "uint256", "name": "lastWinnerIndex", "type": "uint256"},
            {"internalType": "uint256", "name": "participantsCount", "type": "uint256"},
            {"internalType": "uint256", "name": "winnersCount", "type": "uint256"},
            {"internalType": "bool", "name": "exists", "type": "bool"},
            {
                "internalType": "enum AbstractPrizetapRaffle.Status",
                "name": "status",
                "type": "uint8",
            },
            {"internalType": "bytes32", "name": "requirementsHash", "type": "bytes32"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "refundPrize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "refundRemainingPrizes",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "rejectRaffle",
        "outputs": [],
        "stateMutability": "nonpayable",
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
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "expirationTime", "type": "uint256"},
            {"internalType": "uint256[]", "name": "randomNumbers", "type": "uint256[]"},
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
        "name": "setRaffleRandomNumbers",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "periodSeconds", "type": "uint256"}
        ],
        "name": "setValidationPeriod",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "toId", "type": "uint256"},
        ],
        "name": "setWinners",
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
        "inputs": [],
        "name": "unpause",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "validationPeriod",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "multiplier", "type": "uint256"},
            {"internalType": "bytes", "name": "reqId", "type": "bytes"},
            {
                "components": [
                    {"internalType": "uint256", "name": "signature", "type": "uint256"},
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "address", "name": "nonce", "type": "address"},
                ],
                "internalType": "struct IMuonClient.SchnorrSign",
                "name": "sign",
                "type": "tuple",
            },
            {"internalType": "bytes", "name": "gatewaySignature", "type": "bytes"},
        ],
        "name": "verifyParticipationSig",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "expirationTime", "type": "uint256"},
            {"internalType": "uint256[]", "name": "randomNumbers", "type": "uint256[]"},
            {"internalType": "bytes", "name": "reqId", "type": "bytes"},
            {
                "components": [
                    {"internalType": "uint256", "name": "signature", "type": "uint256"},
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "address", "name": "nonce", "type": "address"},
                ],
                "internalType": "struct IMuonClient.SchnorrSign",
                "name": "sign",
                "type": "tuple",
            },
            {"internalType": "bytes", "name": "gatewaySignature", "type": "bytes"},
        ],
        "name": "verifyRandomNumberSig",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]
PRIZETAP_ERC721_ABI = [
    {
        "inputs": [
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
            {"internalType": "address", "name": "_admin", "type": "address"},
            {"internalType": "address", "name": "_operator", "type": "address"},
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "multiplier",
                "type": "uint256",
            },
        ],
        "name": "Participate",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "account",
                "type": "address",
            }
        ],
        "name": "Paused",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "winner",
                "type": "address",
            },
        ],
        "name": "PrizeClaimed",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            }
        ],
        "name": "PrizeRefunded",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "initiator",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
        ],
        "name": "RaffleCreated",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "rejector",
                "type": "address",
            },
        ],
        "name": "RaffleRejected",
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
                "internalType": "address",
                "name": "account",
                "type": "address",
            }
        ],
        "name": "Unpaused",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "raffleId",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "fromId",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "toId",
                "type": "uint256",
            },
        ],
        "name": "WinnersSpecified",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "DEFAULT_ADMIN_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "MAX_NUM_WINNERS",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "OPERATOR_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "_ERC721_RECEIVED",
        "outputs": [{"internalType": "bytes4", "name": "", "type": "bytes4"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "claimPrize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "collection", "type": "address"},
            {"internalType": "uint256[]", "name": "tokenIds", "type": "uint256[]"},
            {"internalType": "uint256", "name": "maxParticipants", "type": "uint256"},
            {"internalType": "uint256", "name": "maxMultiplier", "type": "uint256"},
            {"internalType": "uint256", "name": "startTime", "type": "uint256"},
            {"internalType": "uint256", "name": "endTime", "type": "uint256"},
            {"internalType": "uint256", "name": "winnersCount", "type": "uint256"},
            {"internalType": "bytes32", "name": "requirementsHash", "type": "bytes32"},
        ],
        "name": "createRaffle",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "fromId", "type": "uint256"},
            {"internalType": "uint256", "name": "toId", "type": "uint256"},
        ],
        "name": "getParticipants",
        "outputs": [
            {"internalType": "address[]", "name": "participants", "type": "address[]"}
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
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "fromId", "type": "uint256"},
            {"internalType": "uint256", "name": "toId", "type": "uint256"},
        ],
        "name": "getWinners",
        "outputs": [
            {"internalType": "address[]", "name": "winners", "type": "address[]"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "getWinnersCount",
        "outputs": [
            {"internalType": "uint256", "name": "winnersCount", "type": "uint256"}
        ],
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
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "name": "isParticipated",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "address", "name": "", "type": "address"},
        ],
        "name": "isWinner",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "address", "name": "", "type": "address"},
        ],
        "name": "isWinnerClaimed",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "lastNotWinnerIndexes",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "lastRaffleId",
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
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "bytes", "name": "", "type": "bytes"},
        ],
        "name": "onERC721Received",
        "outputs": [{"internalType": "bytes4", "name": "", "type": "bytes4"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "name": "participantPositions",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "multiplier", "type": "uint256"},
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
        "name": "participateInRaffle",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "pause",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "paused",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "name": "raffleParticipants",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "name": "raffleWinners",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "raffles",
        "outputs": [
            {"internalType": "address", "name": "initiator", "type": "address"},
            {"internalType": "address", "name": "collection", "type": "address"},
            {"internalType": "uint256", "name": "maxParticipants", "type": "uint256"},
            {"internalType": "uint256", "name": "maxMultiplier", "type": "uint256"},
            {"internalType": "uint256", "name": "startTime", "type": "uint256"},
            {"internalType": "uint256", "name": "endTime", "type": "uint256"},
            {
                "internalType": "uint256",
                "name": "lastParticipantIndex",
                "type": "uint256",
            },
            {"internalType": "uint256", "name": "lastWinnerIndex", "type": "uint256"},
            {"internalType": "uint256", "name": "participantsCount", "type": "uint256"},
            {"internalType": "uint256", "name": "winnersCount", "type": "uint256"},
            {
                "internalType": "uint256",
                "name": "lastNotClaimedTokenIndex",
                "type": "uint256",
            },
            {"internalType": "bool", "name": "exists", "type": "bool"},
            {
                "internalType": "enum AbstractPrizetapRaffle.Status",
                "name": "status",
                "type": "uint8",
            },
            {"internalType": "bytes32", "name": "requirementsHash", "type": "bytes32"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "refundPrize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "refundRemainingPrizes",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "raffleId", "type": "uint256"}],
        "name": "rejectRaffle",
        "outputs": [],
        "stateMutability": "nonpayable",
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
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "expirationTime", "type": "uint256"},
            {"internalType": "uint256[]", "name": "randomNumbers", "type": "uint256[]"},
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
        "name": "setRaffleRandomNumbers",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "periodSeconds", "type": "uint256"}
        ],
        "name": "setValidationPeriod",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "toId", "type": "uint256"},
        ],
        "name": "setWinners",
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
        "inputs": [],
        "name": "unpause",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "validationPeriod",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "raffleId", "type": "uint256"},
            {"internalType": "uint256", "name": "multiplier", "type": "uint256"},
            {"internalType": "bytes", "name": "reqId", "type": "bytes"},
            {
                "components": [
                    {"internalType": "uint256", "name": "signature", "type": "uint256"},
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "address", "name": "nonce", "type": "address"},
                ],
                "internalType": "struct IMuonClient.SchnorrSign",
                "name": "sign",
                "type": "tuple",
            },
            {"internalType": "bytes", "name": "gatewaySignature", "type": "bytes"},
        ],
        "name": "verifyParticipationSig",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "expirationTime", "type": "uint256"},
            {"internalType": "uint256[]", "name": "randomNumbers", "type": "uint256[]"},
            {"internalType": "bytes", "name": "reqId", "type": "bytes"},
            {
                "components": [
                    {"internalType": "uint256", "name": "signature", "type": "uint256"},
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "address", "name": "nonce", "type": "address"},
                ],
                "internalType": "struct IMuonClient.SchnorrSign",
                "name": "sign",
                "type": "tuple",
            },
            {"internalType": "bytes", "name": "gatewaySignature", "type": "bytes"},
        ],
        "name": "verifyRandomNumberSig",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

UNITAP_PASS_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "approved",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256",
            },
        ],
        "name": "Approval",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "operator",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bool",
                "name": "approved",
                "type": "bool",
            },
        ],
        "name": "ApprovalForAll",
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
                "internalType": "string",
                "name": "baseURI",
                "type": "string",
            }
        ],
        "name": "SetBaseURI",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "from",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "to",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256",
            },
        ],
        "name": "Transfer",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "DEFAULT_ADMIN_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "MINTER_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "baseURI",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "getApproved",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
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
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "operator", "type": "address"},
        ],
        "name": "isApprovedForAll",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "ownerOf",
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
        "inputs": [{"internalType": "address", "name": "to", "type": "address"}],
        "name": "safeMint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "from", "type": "address"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
        ],
        "name": "safeTransferFrom",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "from", "type": "address"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
        ],
        "name": "safeTransferFrom",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "operator", "type": "address"},
            {"internalType": "bool", "name": "approved", "type": "bool"},
        ],
        "name": "setApprovalForAll",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "baseURI_", "type": "string"}],
        "name": "setBaseURI",
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
        "inputs": [],
        "name": "symbol",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "tokenIdCounter",
        "outputs": [
            {"internalType": "uint256", "name": "idCounter", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "from", "type": "address"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
        ],
        "name": "transferFrom",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

VRF_CLIENT_ABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_chainlinkVRFCoordinator",
                "type": "address",
            },
            {
                "internalType": "uint64",
                "name": "_chainlinkVRFSubscriptionId",
                "type": "uint64",
            },
            {"internalType": "bytes32", "name": "_chainlinkKeyHash", "type": "bytes32"},
            {"internalType": "address", "name": "_admin", "type": "address"},
            {"internalType": "address", "name": "_operator", "type": "address"},
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "have", "type": "address"},
            {"internalType": "address", "name": "want", "type": "address"},
        ],
        "name": "OnlyCoordinatorCanFulfill",
        "type": "error",
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
                "name": "requestId",
                "type": "uint256",
            },
            {
                "indexed": False,
                "internalType": "uint256[]",
                "name": "randomWords",
                "type": "uint256[]",
            },
        ],
        "name": "VRFRequestFulfilled",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "requestId",
                "type": "uint256",
            }
        ],
        "name": "VRFRequestSent",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "DEFAULT_ADMIN_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "OPERATOR_ROLE",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "callbackGasLimit",
        "outputs": [{"internalType": "uint32", "name": "", "type": "uint32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "chainlinkKeyHash",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "chainlinkVrfSubscriptionId",
        "outputs": [{"internalType": "uint64", "name": "", "type": "uint64"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "requestId", "type": "uint256"}],
        "name": "getRandomWords",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
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
        "name": "lastRequestId",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "requestId", "type": "uint256"},
            {"internalType": "uint256[]", "name": "randomWords", "type": "uint256[]"},
        ],
        "name": "rawFulfillRandomWords",
        "outputs": [],
        "stateMutability": "nonpayable",
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
        "inputs": [{"internalType": "uint32", "name": "numWords", "type": "uint32"}],
        "name": "requestRandomWords",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
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
        "inputs": [{"internalType": "uint32", "name": "gaslimit", "type": "uint32"}],
        "name": "setCallbackGasLimit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "period", "type": "uint256"}],
        "name": "setValidityPeriod",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "keyHash", "type": "bytes32"}],
        "name": "setVrfKeyHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint16", "name": "count", "type": "uint16"}],
        "name": "setVrfRequestConfirmations",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint64", "name": "id", "type": "uint64"}],
        "name": "setVrfSubscriptionId",
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
        "inputs": [],
        "name": "validityPeriod",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "vrfRequestConfirmations",
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "vrfRequests",
        "outputs": [
            {"internalType": "uint256", "name": "expirationTime", "type": "uint256"},
            {"internalType": "uint256", "name": "numWords", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

VRF_CLIENT_POLYGON_ADDRESS = "0xd713f3584EADc92848d64C31fD66CD50AdF272CD"
VRF_CLIENT_BSCTEST_ADDRESS = "0xb8B0c04282d9c55cb17d7ef0bF56ef3Bbe203F3C"

match DEPLOYMENT_ENV:
    case "main":
        CONTRACT_ADDRESSES = {
            "42161": {
                "erc20_prizetap_addr": "0xeb1Ad34EA13aF7Ec73Bb872F3Ab2B9250d62b7FD",
                "erc721_prizetap_addr": "0xAaBD83213d545180eeC498877Aa7891E232FCE59",
            },
            "10": {
                "erc20_prizetap_addr": "0xeb1Ad34EA13aF7Ec73Bb872F3Ab2B9250d62b7FD",
                "erc721_prizetap_addr": "0xAaBD83213d545180eeC498877Aa7891E232FCE59",
            },
            "59144": {
                "erc20_prizetap_addr": "0xeb1Ad34EA13aF7Ec73Bb872F3Ab2B9250d62b7FD",
                "erc721_prizetap_addr": "0xAaBD83213d545180eeC498877Aa7891E232FCE59",
            },
            "8453": {
                "erc20_prizetap_addr": "0xeb1Ad34EA13aF7Ec73Bb872F3Ab2B9250d62b7FD",
                "erc721_prizetap_addr": "0xAaBD83213d545180eeC498877Aa7891E232FCE59",
            },
            "7777777": {
                "erc20_prizetap_addr": "0xeb1Ad34EA13aF7Ec73Bb872F3Ab2B9250d62b7FD",
                "erc721_prizetap_addr": "0xAaBD83213d545180eeC498877Aa7891E232FCE59",
            },
            "137": {
                "erc20_prizetap_addr": "0xeb1Ad34EA13aF7Ec73Bb872F3Ab2B9250d62b7FD",
                "erc721_prizetap_addr": "0xAaBD83213d545180eeC498877Aa7891E232FCE59",
            },
        }
    case "dev":
        CONTRACT_ADDRESSES = {
            "97": {"erc20_prizetap_addr": "0x183390bE36EA575D93b5651c36cFe73DF642eD1b"},
        }
    case _:
        CONTRACT_ADDRESSES = {}
