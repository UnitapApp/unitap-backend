from django.urls import reverse
from authentication.models import NetworkTypes, UserProfile
from faucet.models import Chain, WalletAccount
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.utils import timezone
from tokenTap.models import TokenDistribution, TokenDistributionClaim


test_wallet_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
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

    def test_token_distribution_creation(self):
        td = TokenDistribution.objects.create(
            name="Test Distribution",
            distributer="Test Distributer",
            distributer_url="https://example.com/distributer",
            discord_url="https://discord.com/example",
            twitter_url="https://twitter.com/example",
            image_url="https://example.com/image.png",
            token="TEST",
            token_address="0x123456789abcdef",
            amount=1000,
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=7),
        )

        self.assertEqual(TokenDistribution.objects.count(), 1)
        self.assertEqual(TokenDistribution.objects.first(), td)

    def test_token_distribution_expiration(self):
        td1 = TokenDistribution.objects.create(
            name="Test Distribution",
            distributer="Test Distributer",
            distributer_url="https://example.com/distributer",
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
            distributer="Test Distributer",
            distributer_url="https://example.com/distributer",
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
            distributer="Test Distributer",
            distributer_url="https://example.com/distributer",
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
            signed_typed_data="0x123456789abcdef",
        )

        self.assertEqual(TokenDistributionClaim.objects.count(), 1)
        self.assertEqual(TokenDistributionClaim.objects.first(), tdc)
