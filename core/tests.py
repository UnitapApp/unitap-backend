from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from authentication.models import GitcoinPassportConnection, UserProfile, Wallet
from core.models import Chain, NetworkTypes, WalletAccount

from django.test import TestCase, RequestFactory
from unittest.mock import patch
from core.telegram import LogMiddleware

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
        self.minimum = 10

        self.gp = GitcoinPassportConnection.objects.create(
            user_wallet_address=self.address, user_profile=self.user_profile
        )

        self.not_connected_user_profile = UserProfile.objects.create(
            user=User.objects.create_user(username="newtest", password="1234"),
            initial_context_id="newtest",
            username="newtest",
        )
        self.not_connected_address = "0x319B32d11e29dB4a6dB9E4E3da91Fc7FA2D2ff92"
        create_new_wallet(
            user_profile=self.not_connected_user_profile,
            _address=self.not_connected_address,
            wallet_type="EVM",
        )

    def test_gitcoin_passport_minimum_score_constraint_success(self):
        constraint = HasMinimumHumanityScore(self.user_profile)

        constraint.param_values = {
            "MINIMUM": self.minimum,
        }

        self.assertEqual(constraint.is_observed(), True)

    def test_gitcoin_passport_minimum_score_constraint_fail_on_connection(self):
        constraint = HasMinimumHumanityScore(self.not_connected_user_profile)

        constraint.param_values = {
            "MINIMUM": self.minimum,
        }

        self.assertEqual(constraint.is_observed(), False)

    def test_gitcoin_passport_minimum_score_constraint_fail_on_minimum(self):
        constraint = HasMinimumHumanityScore(self.not_connected_user_profile)

        constraint.param_values = {
            "MINIMUM": 30,
        }

        self.assertEqual(constraint.is_observed(), False)

    def test_gitcoin_passport_connection_constraint_success(self):
        constraint = HasGitcoinPassportProfile(self.user_profile)

        self.assertEqual(constraint.is_observed(), True)

    def test_gitcoin_passport_connection_constraint_fail(self):
        constraint = HasGitcoinPassportProfile(self.not_connected_user_profile)

        self.assertEqual(constraint.is_observed(), False)





class LogMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = LogMiddleware()

    @patch("your_project_name.telegram.send_telegram_log")
    def test_log_message_sent_to_telegram(self, mock_send_telegram_log):
        # Mock the current time
        with patch("time.time", return_value=1000000):
            request = self.factory.get("/")
            response = self.factory.get_response("/")

            # Simulate processing a request
            self.middleware.process_request(request)
            self.middleware.log_message("Test log message")

            # Ensure the send_telegram_log function was called
            mock_send_telegram_log.assert_called_once_with("Test log message")

    @patch("your_project_name.telegram.send_telegram_log")
    def test_log_message_not_sent_within_one_hour(self, mock_send_telegram_log):
        # Mock the current time
        with patch("time.time", side_effect=[1000000, 1000000 + 3599]):
            request = self.factory.get("/")
            response = self.factory.get_response("/")

            # Simulate processing a request and logging a message
            self.middleware.process_request(request)
            self.middleware.log_message("Test log message")

            # Simulate another request within one hour
            self.middleware.process_request(request)
            self.middleware.log_message("Test log message")

            # Ensure the send_telegram_log function was called only once
            mock_send_telegram_log.assert_called_once_with("Test log message")

    @patch("your_project_name.telegram.send_telegram_log")
    def test_log_message_sent_after_one_hour(self, mock_send_telegram_log):
        # Mock the current time
        with patch("time.time", side_effect=[1000000, 1000000 + 3601]):
            request = self.factory.get("/")
            response = self.factory.get_response("/")

            # Simulate processing a request and logging a message
            self.middleware.process_request(request)
            self.middleware.log_message("Test log message")

            # Simulate another request after more than one hour
            self.middleware.process_request(request)
            self.middleware.log_message("Test log message")

            # Ensure the send_telegram_log function was called twice
            self.assertEqual(mock_send_telegram_log.call_count, 2)

    @patch("your_project_name.telegram.send_telegram_log")
    def test_middleware_handles_requests(self, mock_send_telegram_log):
        request = self.factory.get("/")
        response = self.factory.get_response("/")

        # Simulate processing a request
        self.middleware.process_request(request)

        # Ensure that no log message was sent
        mock_send_telegram_log.assert_not_called()

