from unittest.mock import patch
from django.urls import reverse
from authentication.models import NetworkTypes, UserProfile, Wallet
from faucet.faucet_manager.credit_strategy import WeeklyCreditStrategy
from faucet.models import Chain, GlobalSettings, WalletAccount
from django.contrib.auth.models import User
from permissions.models import (
    BrightIDAuraVerification,
    BrightIDMeetVerification,
    OncePerWeekVerification,
    OncePerMonthVerification,
)
from rest_framework.test import APITestCase
import inspect
from .helpers import create_uint32_random_nonce, hash_message, sign_hashed_message
from django.utils import timezone
from tokenTap.models import TokenDistribution, TokenDistributionClaim


test_wallet_key = "f57fecd11c6034fd2665d622e866f05f9b07f35f253ebd5563e3d7e76ae66809"
test_rpc_url_private = "http://ganache:7545"
fund_manager = "0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0"
x_dai_max_claim = 800e6
gnosis_tokentap_contract_address = "0xB67ec856346b22e4BDA2ab2B53d70D61a2014358"


class TokenDistributionTestCase(APITestCase):
    def setUp(self):
        self.chain = Chain.objects.create(
            chain_name="Gnosis Chain",
            wallet=WalletAccount.objects.create(
                name="Gnosis Chain Wallet",
                private_key=test_wallet_key,
                network_type=NetworkTypes.EVM,
            ),
            rpc_url_private=test_rpc_url_private,
            fund_manager_address=fund_manager,
            native_currency_name="xdai",
            symbol="XDAI",
            chain_id="100",
            max_claim_amount=x_dai_max_claim,
            tokentap_contract_address=gnosis_tokentap_contract_address,
        )

        self.permission = BrightIDMeetVerification.objects.create(
            name="BrightID Meet Verification"
        )

    def test_token_distribution_creation(self):
        td = TokenDistribution.objects.create(
            name="Test Distribution",
            distributor="Test distributor",
            distributor_url="https://example.com/distributor",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x123456789abcdef",
            amount=1000,
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=7),
            # permissions=[self.permission],
        )
        td.permissions.set([self.permission])

        self.assertEqual(TokenDistribution.objects.count(), 1)
        self.assertEqual(TokenDistribution.objects.first(), td)
        self.assertEqual(TokenDistribution.objects.first().permissions.count(), 1)
        self.assertEqual(
            TokenDistribution.objects.first().permissions.first(), self.permission
        )

    def test_token_distribution_expiration(self):
        td1 = TokenDistribution.objects.create(
            name="Test Distribution",
            distributor="Test distributor",
            distributor_url="https://example.com/distributor",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x123456789abcdef",
            amount=1000,
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=7),
        )
        self.assertFalse(td1.is_expired)

        td2 = TokenDistribution.objects.create(
            name="Test Distribution",
            distributor="Test distributor",
            distributor_url="https://example.com/distributor",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x123456789abcdef",
            amount=1000,
            chain=self.chain,
            deadline=timezone.now() - timezone.timedelta(days=7),
        )
        self.assertTrue(td2.is_expired)


class TokenDistributionClaimTestCase(APITestCase):
    def setUp(self) -> None:

        self.userprofile = UserProfile.objects.create(
            user=User.objects.create_user(username="testuser", password="testpassword"),
            initial_context_id="testuser",
            username="testuser",
        )

        self.chain = Chain.objects.create(
            chain_name="Gnosis Chain",
            wallet=WalletAccount.objects.create(
                name="Gnosis Chain Wallet",
                private_key=test_wallet_key,
                network_type=NetworkTypes.EVM,
            ),
            rpc_url_private=test_rpc_url_private,
            fund_manager_address=fund_manager,
            native_currency_name="xdai",
            symbol="XDAI",
            chain_id="100",
            max_claim_amount=x_dai_max_claim,
            tokentap_contract_address=gnosis_tokentap_contract_address,
        )

        self.td = TokenDistribution.objects.create(
            name="Test Distribution",
            distributor="Test distributor",
            distributor_url="https://example.com/distributor",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x123456789abcdef",
            amount=1000,
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=7),
        )

    def test_token_distribution_claim_creation(self):

        tdc = TokenDistributionClaim.objects.create(
            user_profile=self.userprofile,
            token_distribution=self.td,
            nonce=1,
            signature="0x123456789abcdef",
        )

        self.assertEqual(TokenDistributionClaim.objects.count(), 1)
        self.assertEqual(TokenDistributionClaim.objects.first(), tdc)


class TokenDistributionAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.global_settings = GlobalSettings.objects.create()

        self.chain = Chain.objects.create(
            chain_name="Gnosis Chain",
            wallet=WalletAccount.objects.create(
                name="Gnosis Chain Wallet",
                private_key=test_wallet_key,
                network_type=NetworkTypes.EVM,
            ),
            rpc_url_private=test_rpc_url_private,
            fund_manager_address=fund_manager,
            native_currency_name="xdai",
            explorer_url="https://blockscout.com/poa/xdai/",
            symbol="XDAI",
            chain_id="100",
            max_claim_amount=x_dai_max_claim,
            tokentap_contract_address=gnosis_tokentap_contract_address,
        )

        self.user_profile = UserProfile.objects.get_or_create("mamad")

        self.td = TokenDistribution.objects.create(
            name="Test Distribution",
            distributor="Test distributor",
            distributor_url="https://example.com/distributor",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x83ff60e2f93f8edd0637ef669c69d5fb4f64ca8e",
            amount=1000,
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=7),
            max_number_of_claims=100,
            notes="Test Notes",
        )
        self.permission1 = BrightIDMeetVerification.objects.create(
            name="BrightID Meet Verification",
            description="Verify that you have met the distributor in person.",
        )
        self.permission2 = BrightIDAuraVerification.objects.create(
            name="BrightID Aura Verification",
            description="Verify that you have a high Aura score.",
        )
        self.permission3 = OncePerWeekVerification.objects.create(
            name="Once Per Week Verification",
            description="Verify that you have not claimed from this distribution in the last week.",
        )
        self.permission4 = OncePerMonthVerification.objects.create(
            name="Once Per Month Verification",
            description="Verify that you have not claimed from this distribution in the last month.",
        )

        self.td.permissions.set(
            [self.permission1, self.permission2, self.permission3, self.permission4]
        )

    def test_token_distribution_list(self):
        response = self.client.get(reverse("token-distribution-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Distribution")
        self.assertEqual(
            response.data[0]["permissions"][0]["name"], "BrightID Meet Verification"
        )
        self.assertEqual(
            response.data[0]["permissions"][1]["name"], "BrightID Aura Verification"
        )

    def test_token_distribution_not_claimable_max_reached(self):
        ltd = TokenDistribution.objects.create(
            name="Test Distribution",
            distributor="Test distributor",
            distributor_url="https://example.com/distributor",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x123456789abcdef",
            amount=1000,
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=7),
            max_number_of_claims=0,
            notes="Test Notes",
        )

        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": ltd.pk}),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "This token is not claimable")

    def test_token_distribution_not_claimable_deadline_reached(self):
        ltd = TokenDistribution.objects.create(
            name="Test Distribution",
            distributor="Test distributor",
            distributor_url="https://example.com/distributor",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x123456789abcdef",
            amount=1000,
            chain=self.chain,
            deadline=timezone.now() - timezone.timedelta(days=7),
            max_number_of_claims=10,
            notes="Test Notes",
        )

        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": ltd.pk}),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "This token is not claimable")

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_token_distribution_not_claimable_already_claimed(self):
        tdc = TokenDistributionClaim.objects.create(
            user_profile=self.user_profile,
            token_distribution=self.td,
        )

        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk}),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "You have already claimed this token this week."
        )

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_token_distribution_not_claimable_already_claimed_month(self):
        tdc = TokenDistributionClaim.objects.create(
            user_profile=self.user_profile,
            token_distribution=self.td,
            # Claimed 2 weeks ago
            created_at=WeeklyCreditStrategy.get_second_last_monday(),
        )
        tdc.created_at = WeeklyCreditStrategy.get_second_last_monday()
        tdc.save()

        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk}),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "You have already claimed this token this month."
        )

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (False, None),
    )
    def test_token_distribution_not_claimable_false_permissions(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_token_distribution_not_claimable_weekly_credit_limit_reached(self):
        self.global_settings.tokentap_weekly_claim_limit = 0
        self.global_settings.save()

        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk}),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "You have reached your weekly claim limit"
        )

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_token_distribution_not_claimable_no_wallet(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk})
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "You have not connected an EVM wallet to your account",
        )

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_token_distribution_claimable(self):

        Wallet.objects.create(
            user_profile=self.user_profile,
            wallet_type=NetworkTypes.EVM,
            address="0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb",
        )
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk})
        )

        self.assertEqual(response.status_code, 200)


class HelpersTestCase(APITestCase):
    def test_nonce_creator(self):
        n1 = create_uint32_random_nonce()
        n2 = create_uint32_random_nonce()
        n3 = create_uint32_random_nonce()

        self.assertNotEqual(n1, n2)
        self.assertNotEqual(n1, n3)
        self.assertNotEqual(n2, n3)

    def test_sign_message(self):
        wallet = WalletAccount.objects.create(
            name="Gnosis Chain Wallet",
            private_key=test_wallet_key,
            network_type=NetworkTypes.EVM,
        )

        hash = hash_message(
            user="0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb",
            token="0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb",
            amount=100000000000000000,
            nonce=create_uint32_random_nonce(),
        )

        sig = sign_hashed_message(hashed_message=hash)
        from web3 import Web3

        recovered_address = Web3().eth.account.recover_message(hash, signature=sig)
        self.assertTrue(recovered_address.lower() == wallet.address.lower())


class TokenDistributionClaimAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.chain = Chain.objects.create(
            chain_name="Gnosis Chain",
            wallet=WalletAccount.objects.create(
                name="Gnosis Chain Wallet",
                private_key=test_wallet_key,
                network_type=NetworkTypes.EVM,
            ),
            rpc_url_private=test_rpc_url_private,
            fund_manager_address=fund_manager,
            native_currency_name="xdai",
            explorer_url="https://blockscout.com/poa/xdai/",
            symbol="XDAI",
            chain_id="100",
            max_claim_amount=x_dai_max_claim,
            tokentap_contract_address=gnosis_tokentap_contract_address,
        )

        self.user_profile = UserProfile.objects.get_or_create("mamad")

        self.td = TokenDistribution.objects.create(
            name="Test Distribution",
            distributor="Test distributor",
            distributor_url="https://example.com/distributor",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x83ff60e2f93f8edd0637ef669c69d5fb4f64ca8e",
            amount=1000,
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=7),
            max_number_of_claims=100,
            notes="Test Notes",
        )
        self.permission1 = BrightIDMeetVerification.objects.create(
            name="BrightID Meet Verification",
            description="Verify that you have met the distributor in person.",
        )
        self.permission2 = BrightIDAuraVerification.objects.create(
            name="BrightID Aura Verification",
            description="Verify that you have a high Aura score.",
        )
        self.td.permissions.set([self.permission1, self.permission2])

        self.tdc = TokenDistributionClaim.objects.create(
            user_profile=self.user_profile,
            token_distribution=self.td,
            nonce=1,
            signature="0x0000000",
        )

    def test_token_distribution_claim_list(self):
        self.client.force_authenticate(user=self.user_profile.user)

        response = self.client.get(reverse("claims-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["token_distribution"]["id"], self.td.pk)

    def test_token_distribution_claim_retrieve(self):
        self.client.force_authenticate(user=self.user_profile.user)

        response = self.client.get(
            reverse("claim-retrieve", kwargs={"pk": self.tdc.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["token_distribution"]["id"], self.td.pk)
