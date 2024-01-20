from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from authentication.models import UserProfile, Wallet
from core.models import Chain, NetworkTypes, WalletAccount

from .constraints import (
    BrightIDAuraVerification,
    BrightIDMeetVerification,
    HasNFTVerification,
    HasTokenVerification,
)

test_wallet_key = "f57fecd11c6034fd2665d622e866f05f9b07f35f253ebd5563e3d7e76ae66809"


def create_new_wallet(user_profile, _address, wallet_type) -> Wallet:
    wallet, is_create = Wallet.objects.get_or_create(
        user_profile=user_profile, address=_address, wallet_type=wallet_type
    )
    return wallet


class BaseTestCase(APITestCase):
    def setUp(self):
        self.user_profile = UserProfile.objects.create(
            user=User.objects.create_user(username="test", password="1234"),
            initial_context_id="test",
            username="test",
        )


class ConstraintTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    @patch(
        "authentication.models.UserProfile.is_meet_verified", new_callable=PropertyMock
    )
    def test_meet_constraint(self, is_meet_verified_mock: PropertyMock):
        is_meet_verified_mock.return_value = False
        constraint = BrightIDMeetVerification(self.user_profile)
        self.assertEqual(constraint.is_observed(), False)
        self.assertEqual(
            constraint.response, "BrightIDMeetVerification constraint is violated"
        )

    @patch(
        "authentication.models.UserProfile.is_aura_verified", new_callable=PropertyMock
    )
    def test_aura_constraint(self, is_aura_verified_mock: PropertyMock):
        is_aura_verified_mock.return_value = False
        constraint = BrightIDAuraVerification(self.user_profile)
        self.assertEqual(constraint.is_observed(), False)
        self.assertEqual(
            constraint.response, "BrightIDAuraVerification constraint is violated"
        )


class TestNFTConstraint(BaseTestCase):
    def setUp(self):
        super().setUp()
        create_new_wallet(
            self.user_profile,
            "0x23826Fd930916718a98A21FF170088FBb4C30803",
            NetworkTypes.EVM,
        )
        create_new_wallet(
            self.user_profile,
            "0x23826Fd930916718a98A21FF170088FBb4C30804",
            NetworkTypes.EVM,
        )
        self.collection_address = "0x23826Fd930916718a98A21FF170088FBb4C30803"
        self.minimum = 1
        self.wallet = WalletAccount.objects.create(
            name="Sepolia Chain Wallet",
            private_key=test_wallet_key,
            network_type=NetworkTypes.EVM,
        )
        self.chain = Chain.objects.create(
            chain_name="Polygon",
            wallet=self.wallet,
            rpc_url_private="https://polygon-rpc.com/",
            explorer_url="https://etherscan.io/",
            native_currency_name="ETH",
            symbol="ETH",
            chain_id="1",
        )

    @patch(
        "core.utils.NFTClient.get_number_of_tokens",
        lambda a, b: 1,
    )
    def test_nft_constraint_true(self):
        constraint = HasNFTVerification(self.user_profile)

        constraint.param_values = {
            "CHAIN": self.chain.pk,
            "COLLECTION_ADDRESS": self.collection_address,
            "MINIMUM": self.minimum,
        }

        self.assertEqual(constraint.is_observed(), True)

    @patch(
        "core.utils.NFTClient.get_number_of_tokens",
        lambda a, b: 0,
    )
    def test_nft_constraint_false(self):
        constraint = HasNFTVerification(self.user_profile)

        constraint.param_values = {
            "CHAIN": self.chain.pk,
            "COLLECTION_ADDRESS": self.collection_address,
            "MINIMUM": 1,
        }

        self.assertEqual(constraint.is_observed(), False)


class TestNonNativeTokenConstraint(BaseTestCase):
    def setUp(self):
        super().setUp()
        create_new_wallet(
            self.user_profile,
            "0x23826Fd930916718a98A21FF170088FBb4C30803",
            NetworkTypes.EVM,
        )
        create_new_wallet(
            self.user_profile,
            "0x23826Fd930916718a98A21FF170088FBb4C30804",
            NetworkTypes.EVM,
        )
        self.address = "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"
        self.minimum = 1000000
        self.wallet = WalletAccount.objects.create(
            name="Sepolia Chain Wallet",
            private_key=test_wallet_key,
            network_type=NetworkTypes.EVM,
        )
        self.chain = Chain.objects.create(
            chain_name="Polygon",
            wallet=self.wallet,
            rpc_url_private="https://polygon-rpc.com/",
            explorer_url="https://etherscan.io/",
            native_currency_name="ETH",
            symbol="ETH",
            chain_id="1",
        )

    @patch(
        "core.utils.TokenClient.get_non_native_token_balance",
        lambda a, b: 1000000,
    )
    def test_non_native_token_constraint_true(self):
        constraint = HasTokenVerification(self.user_profile)

        constraint.param_values = {
            "CHAIN": self.chain.pk,
            "ADDRESS": self.address,
            "MINIMUM": self.minimum,
        }

        self.assertEqual(constraint.is_observed(), True)

    @patch(
        "core.utils.TokenClient.get_non_native_token_balance",
        lambda a, b: 100000,
    )
    def test_non_native_token_constraint_false(self):
        constraint = HasTokenVerification(self.user_profile)

        constraint.param_values = {
            "CHAIN": self.chain.pk,
            "ADDRESS": self.address,
            "MINIMUM": self.minimum,
        }

        self.assertEqual(constraint.is_observed(), False)
