from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from authentication.models import UserProfile, Wallet
from core.models import Chain, NetworkTypes, WalletAccount

from .constraints import (
    Attest,
    BeAttestedBy,
    BrightIDAuraVerification,
    BrightIDMeetVerification,
    HasGitcoinPassportProfile,
    HasMinimumHumanityScore,
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
            "ADDRESS": self.collection_address,
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
            "ADDRESS": self.collection_address,
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

    @patch(
        "core.utils.TokenClient.get_native_token_balance",
        lambda a, b: 2 * 10**18,
    )
    def test_native_token_constraint_true(self):
        constraint = HasTokenVerification(self.user_profile)

        constraint.param_values = {
            "CHAIN": self.chain.pk,
            "ADDRESS": "0x00",
            "MINIMUM": 3 * 10**18,
        }

        self.assertEqual(constraint.is_observed(), True)

    @patch(
        "core.utils.TokenClient.get_native_token_balance",
        lambda a, b: 2 * 10**18,
    )
    def test_native_token_constraint_false(self):
        constraint = HasTokenVerification(self.user_profile)

        constraint.param_values = {
            "CHAIN": self.chain.pk,
            "ADDRESS": "0x0000",
            "MINIMUM": 5 * 10**18,
        }

        self.assertEqual(constraint.is_observed(), False)


class TestBeAttestedByConstraint(BaseTestCase):
    def setUp(self):
        super().setUp()
        create_new_wallet(
            self.user_profile,
            "0xf3c6f3Afb66fCEA5CC6f1Eee51fd26646F89e4e9",
            NetworkTypes.EVM,
        )
        self.address = "0x2D93c2F74b2C4697f9ea85D0450148AA45D4D5a2"
        self.schema_id = (
            "0x3eed14a2055f68d13ad270640208640413b951e12b382b253a08518dedc5172a"
        )
        self.key = "signedUp"
        self.value = "true"
        self.wallet = WalletAccount.objects.create(
            name="Sepolia Chain Wallet",
            private_key=test_wallet_key,
            network_type=NetworkTypes.EVM,
        )
        self.chain = Chain.objects.create(
            chain_name="Optimism",
            wallet=self.wallet,
            rpc_url_private="https://optimism-rpc.com/",
            explorer_url="https://etherscan.io/",
            native_currency_name="ETH",
            symbol="ETH",
            chain_id="1",
        )

    def test_by_attested_by(self):
        constraint = BeAttestedBy(self.user_profile)

        constraint.param_values = {
            "CHAIN": self.chain.pk,
            "ADDRESS": self.address,
            "KEY": self.key,
            "VALUE": self.value,
            "EAS_SCHEMA_ID": self.schema_id,
        }

        self.assertEqual(constraint.is_observed(), True)


class TestEASAttestConstraint(BaseTestCase):
    def setUp(self):
        super().setUp()
        create_new_wallet(
            self.user_profile,
            "0x319B32d11e29dB4a6dB9E4E3da91Fc7FA2D2ff92",
            NetworkTypes.EVM,
        )
        self.address = "0x319B32d11e29dB4a6dB9E4E3da91Fc7FA2D2ff92"
        self.schema_id = (
            "0x3969bb076acfb992af54d51274c5c868641ca5344e1aacd0b1f5e4f80ac0822f"
        )
        self.key = "message"
        self.value = "test"
        self.wallet = WalletAccount.objects.create(
            name="Sepolia Chain Wallet",
            private_key=test_wallet_key,
            network_type=NetworkTypes.EVM,
        )
        self.chain = Chain.objects.create(
            chain_name="Optimism",
            wallet=self.wallet,
            rpc_url_private="https://optimism-rpc.com/",
            explorer_url="https://etherscan.io/",
            native_currency_name="ETH",
            symbol="ETH",
            chain_id="1",
        )

    def test_EAS_attest_constraints(self):
        constraint = Attest(self.user_profile)

        constraint.param_values = {
            "CHAIN": self.chain.pk,
            "ADDRESS": self.address,
            "KEY": self.key,
            "VALUE": self.value,
            "EAS_SCHEMA_ID": self.schema_id,
        }

        self.assertEqual(constraint.is_observed(), True)


class TestGitcoinPassportConstraint(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.address = "0x0cE49AF5d8c5A70Edacd7115084B2b3041fE4fF6"
        self.user_profile = self.user_profile
        create_new_wallet(
            user_profile=self.user_profile, _address=self.address, wallet_type="EVM"
        )
        self.minimum = 1

        self.client.force_authenticate(user=self.user_profile.user)
        self.client.post(
            reverse("AUTHENTICATION:connect-gitcoin-passport"),
            data={"user_wallet_address": self.address},
        )

    def test_gitcoin_passport_minimum_score_constraint(self):
        constraint = HasMinimumHumanityScore(self.user_profile)

        constraint.param_values = {
            "MINIMUM": self.minimum,
        }

        self.assertEqual(constraint.is_observed(), True)

    def test_gitcoin_passport_connection_constraint(self):
        constraint = HasGitcoinPassportProfile(self.user_profile)

        self.assertEqual(constraint.is_observed(), True)
