from unittest.mock import patch

# from brightIDfaucet.settings import IS_TESTING
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, override_settings

from authentication.models import NetworkTypes, UserProfile, Wallet
from faucet.models import (
    Chain,
    ClaimReceipt,
    GlobalSettings,
    TransactionBatch,
    WalletAccount,
)
from tokenTap.models import Constraint, TokenDistribution, TokenDistributionClaim

from .helpers import create_uint32_random_nonce, hash_message, sign_hashed_message

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

        self.permission = Constraint.objects.create(
            name="core.BrightIDMeetVerification", title="BrightID Meet", type="VER"
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


@override_settings(IS_TESTING=True)
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

        self.btc_chain = Chain.objects.create(
            chain_name="Bitcoin",
            wallet=WalletAccount.objects.create(
                name="Bitcoin Wallet",
                private_key=test_wallet_key,
                network_type=NetworkTypes.LIGHTNING,
            ),
            rpc_url_private=test_rpc_url_private,
            fund_manager_address=fund_manager,
            native_currency_name="bitcoin",
            explorer_url="https://blockstream.info/testnet/",
            symbol="BTC",
            chain_id="1010",
            max_claim_amount=100,
            chain_type=NetworkTypes.LIGHTNING,
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
        self.permission1 = Constraint.objects.create(
            name="core.BrightIDMeetVerification", title="BrightID Meet", type="VER"
        )
        self.permission2 = Constraint.objects.create(
            name="core.BrightIDAuraVerification", title="BrightID Aura", type="VER"
        )
        self.permission4 = Constraint.objects.create(
            name="tokenTap.OncePerMonthVerification",
            title="Once per Month",
            type="TIME",
        )
        self.permission5 = Constraint.objects.create(
            name="tokenTap.OnceInALifeTimeVerification",
            title="Once per Lifetime",
            type="TIME",
        )

        self.td.permissions.set([self.permission1, self.permission2, self.permission4])

        self.btc_td = TokenDistribution.objects.create(
            name="Test Distribution",
            distributor="Test distributor",
            distributor_url="https://example.com/distributor",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x83ff60e2f93f8edd0637ef669c69d5fb4f64ca8e",
            amount=100,
            chain=self.btc_chain,
            deadline=timezone.now() + timezone.timedelta(days=7),
            max_number_of_claims=10,
            notes="Test Notes",
        )
        self.btc_td.permissions.set([self.permission1, self.permission5])

    def test_token_distribution_list(self):
        response = self.client.get(reverse("token-distribution-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Test Distribution")
        self.assertEqual(
            response.data[0]["permissions"][0]["name"], "core.BrightIDMeetVerification"
        )
        self.assertEqual(
            response.data[0]["permissions"][1]["name"], "core.BrightIDAuraVerification"
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
            data={"user_wallet_address": "0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb"},
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
            data={"user_wallet_address": "0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "This token is not claimable")

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_token_distribution_not_claimable_already_claimed(self):
        TokenDistributionClaim.objects.create(
            user_profile=self.user_profile,
            token_distribution=self.td,
        )

        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk}),
            data={"user_wallet_address": "0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb"},
        )

        self.assertEqual(response.status_code, 403)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (False, None),
    )
    def test_token_distribution_not_claimable_false_permissions(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk}),
            data={"user_wallet_address": "0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb"},
        )

        self.assertEqual(response.status_code, 403)

    def test_token_distribution_not_claimable_weekly_credit_limit_reached(self):
        self.global_settings.tokentap_round_claim_limit = 0
        self.global_settings.save()

        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk}),
            data={"user_wallet_address": "0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb"},
        )

        self.assertEqual(response.status_code, 403)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_token_distribution_not_claimable_no_wallet(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk}),
            data={"user_wallet_address": "0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "This wallet is not registered for this user",
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
            reverse("token-distribution-claim", kwargs={"pk": self.td.pk}),
            data={"user_wallet_address": "0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb"},
        )

        self.assertEqual(response.status_code, 200)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_btc_lightning_claimable(self):
        Wallet.objects.create(
            user_profile=self.user_profile,
            wallet_type=NetworkTypes.EVM,
            address="0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb",
        )
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.btc_td.pk}),
            data={"user_wallet_address": "test"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["signature"]["status"], "Pending")
        self.assertEqual(ClaimReceipt.objects.count(), 1)
        self.assertEqual(ClaimReceipt.objects.first().chain, self.btc_td.chain)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_btc_lightning_claimable_claim_updates_after_6seconds(self):
        Wallet.objects.create(
            user_profile=self.user_profile,
            wallet_type=NetworkTypes.EVM,
            address="0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb",
        )
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("token-distribution-claim", kwargs={"pk": self.btc_td.pk}),
            data={"user_wallet_address": "test"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["signature"]["status"], "Pending")
        self.assertEqual(ClaimReceipt.objects.count(), 1)
        gas_tap_claim = ClaimReceipt.objects.first()
        self.assertEqual(gas_tap_claim.chain, self.btc_td.chain)
        self.assertEqual(gas_tap_claim._status, ClaimReceipt.PENDING)

        tb = TransactionBatch.objects.create(
            chain=self.btc_td.chain, tx_hash="test hash", _status=ClaimReceipt.VERIFIED
        )

        gas_tap_claim.batch = tb
        gas_tap_claim._status = ClaimReceipt.VERIFIED
        gas_tap_claim.save()

        from faucet.tasks import update_tokentap_claim_for_verified_lightning_claims

        update_tokentap_claim_for_verified_lightning_claims.apply()

        gas_tap_claim.refresh_from_db()
        self.assertEqual(gas_tap_claim._status, ClaimReceipt.PROCESSED_FOR_TOKENTAP)
        self.assertEqual(gas_tap_claim.tx_hash, "test hash")
        self.assertEqual(
            TokenDistributionClaim.objects.first().status, ClaimReceipt.VERIFIED
        )
        self.assertEqual(TokenDistributionClaim.objects.first().tx_hash, "test hash")


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
            address="0xc1cbb2ab97260a8a7d4591045a9fb34ec14e87fb",
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
        self.permission1 = Constraint.objects.create(
            name="core.BrightIDMeetVerification", title="BrightID Meet", type="VER"
        )
        self.permission2 = Constraint.objects.create(
            name="core.BrightIDAuraVerification", title="BrightID Aura", type="VER"
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

    # Tests that the token distribution claim status is successfully updated
    def test_successful_update(self):
        claim = TokenDistributionClaim.objects.create(
            token_distribution=TokenDistribution.objects.create(
                token_address="0x123", amount=100, chain=self.chain
            ),
            user_profile=self.user_profile,
            status=ClaimReceipt.PENDING,
        )
        self.client.force_authenticate(user=self.user_profile.user)
        url = reverse("claim-update", kwargs={"pk": claim.pk})
        data = {"tx_hash": "0xabc"}
        response = self.client.post(url, data=data)
        assert response.status_code == 200
        claim.refresh_from_db()
        assert claim.status == ClaimReceipt.VERIFIED
        assert claim.tx_hash == "0xabc"

    # Tests that an error is raised when tx_hash is missing from request data
    def test_missing_tx_hash(self):
        claim = TokenDistributionClaim.objects.create(
            token_distribution=TokenDistribution.objects.create(
                token_address="0x123", amount=100, chain=self.chain
            ),
            user_profile=self.user_profile,
            status=ClaimReceipt.PENDING,
        )
        self.client.force_authenticate(user=self.user_profile.user)
        url = reverse("claim-update", kwargs={"pk": claim.pk})
        data = {}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        assert "tx_hash is a required field" in str(response.content)

    # Tests that an error is raised when the td claim does not belong to the user
    def test_claim_not_belonging_to_user_profile(self):
        other_user_profile = UserProfile.objects.get_or_create("other")
        claim = TokenDistributionClaim.objects.create(
            token_distribution=TokenDistribution.objects.create(
                token_address="0x123", amount=100, chain=self.chain
            ),
            user_profile=other_user_profile,
            status=ClaimReceipt.PENDING,
        )
        self.client.force_authenticate(user=self.user_profile.user)
        url = reverse("claim-update", kwargs={"pk": claim.pk})
        data = {"tx_hash": "0xabc"}
        response = self.client.post(url, data=data)
        assert response.status_code == 403

    # Tests that an error is raised when the tdclaim status is already verified
    def test_already_verified_claim(self):
        claim = TokenDistributionClaim.objects.create(
            token_distribution=TokenDistribution.objects.create(
                token_address="0x123", amount=100, chain=self.chain
            ),
            user_profile=self.user_profile,
            status=ClaimReceipt.VERIFIED,
        )
        self.client.force_authenticate(user=self.user_profile.user)
        url = reverse("claim-update", kwargs={"pk": claim.pk})
        data = {"tx_hash": "0xabc"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 403)
        assert "already been updated" in str(response.content)
