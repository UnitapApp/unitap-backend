{
    "detail": "Signature Created Successfully",
    "signature": {
        "id": 1,
        "token_distribution": OrderedDict(
            [
                ("id", 2),
                ("name", "Test Distribution"),
                ("distributor", "Test distributor"),
                ("distributor_url", "https://example.com/distributor"),
                ("discord_url", "https://discord.com/example"),
                ("twitter_url", "https://twitter.com/example"),
                ("image_url", "https://example.com/image.png"),
                ("token", "TEST"),
                ("token_address", "0x83ff60e2f93f8edd0637ef669c69d5fb4f64ca8e"),
                ("amount", 100),
                (
                    "chain",
                    OrderedDict(
                        [
                            ("pk", 2),
                            ("chain_name", "Bitcoin"),
                            ("chain_id", "1010"),
                            (
                                "fund_manager_address",
                                "0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0",
                            ),
                            ("native_currency_name", "bitcoin"),
                            ("symbol", "BTC"),
                            ("decimals", 18),
                            ("explorer_url", "https://blockstream.info/testnet/"),
                            ("rpc_url", None),
                            ("logo_url", None),
                            ("modal_url", None),
                            ("gas_image_url", None),
                            ("max_claim_amount", 100),
                            ("is_testnet", False),
                            (
                                "tokentap_contract_address",
                                "0xB67ec856346b22e4BDA2ab2B53d70D61a2014358",
                            ),
                            ("chain_type", "EVM"),
                            (
                                "block_scan_address",
                                "https://blockstream.info/testnet/address/0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0",
                            ),
                        ]
                    ),
                ),
                (
                    "permissions",
                    [
                        OrderedDict(
                            [
                                ("id", 1),
                                ("name", "BrightID Meet Verification"),
                                (
                                    "description",
                                    "Verify that you have met the distributor in person.",
                                ),
                                ("resourcetype", "BrightIDMeetVerification"),
                            ]
                        ),
                        OrderedDict(
                            [
                                ("id", 5),
                                ("name", "Once In A Life Time Verification"),
                                (
                                    "description",
                                    "Verify that you have not claimed from this distribution before.",
                                ),
                                ("resourcetype", "OnceInALifeTimeVerification"),
                            ]
                        ),
                    ],
                ),
                ("created_at", "2023-06-24T18:41:13.872011Z"),
                ("deadline", "2023-07-01T18:41:13.871801Z"),
                ("max_number_of_claims", 10),
                ("notes", "Test Notes"),
            ]
        ),
        "user_profile": 1,
        "created_at": "2023-06-24T18:41:13.929304Z",
        "payload": {
            "user": "0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb",
            "token": "0x83ff60e2f93f8edd0637ef669c69d5fb4f64ca8e",
            "amount": 100,
            "nonce": 1937405620,
            "signature": "0xc28ef6f1604c89c319b93b757eeaff211962231063ad17108dacd3416e701b326527fadec7da4bbe3d2ed324ef6b395e62be62d1d62fa7ebc1f56d4742a6e1ad1c",
        },
        "status": "Pending",
        "tx_hash": None,
    },
}
