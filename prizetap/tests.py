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
from tokenTap.helpers import (
    create_uint32_random_nonce,
    hash_message,
    sign_hashed_message,
)
from django.utils import timezone
from prizetap.models import Raffle, RaffleEntry


test_wallet_key = "f57fecd11c6034fd2665d622e866f05f9b07f35f253ebd5563e3d7e76ae66809"
test_rpc_url_private = "http://ganache:7545"
fund_manager = "0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0"
x_dai_max_claim = 800e6
gnosis_tokentap_contract_address = "0xB67ec856346b22e4BDA2ab2B53d70D61a2014358"


# Create your tests here.


class RaffleTestCase(APITestCase):
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

    def test_raffle_creation(self):
        raffle = Raffle.objects.create(
            name="Test Raffle",
            description="Test Raffle Description",
            creator="Test Creator",
            is_prize_nft=False,
            prize="Test Prize",
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=1),
            max_number_of_entries=100,
        )

        raffle.permissions.set([self.permission])

        self.assertEqual(Raffle.objects.count(), 1)
        self.assertEqual(Raffle.objects.first(), raffle)
        self.assertEqual(Raffle.objects.first().permissions.count(), 1)
        self.assertEqual(Raffle.objects.first().permissions.first(), self.permission)

    def test_raffle_expiration(self):
        raffle = Raffle.objects.create(
            name="Test Raffle",
            description="Test Raffle Description",
            creator="Test Creator",
            is_prize_nft=False,
            prize="Test Prize",
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=1),
            max_number_of_entries=100,
        )

        self.assertFalse(raffle.is_expired)

        raffle.deadline = timezone.now() - timezone.timedelta(days=1)
        raffle.save()

        self.assertTrue(raffle.is_expired)


class RaffleAPITestCase(APITestCase):
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
            symbol="XDAI",
            chain_id="100",
            explorer_url="https://blockscout.com/poa/xdai/",
            max_claim_amount=x_dai_max_claim,
            tokentap_contract_address=gnosis_tokentap_contract_address,
        )

        self.permission = BrightIDMeetVerification.objects.create(
            name="BrightID Meet Verification"
        )
        self.permission2 = BrightIDAuraVerification.objects.create(
            name="BrightID Aura Verification"
        )

        raffle = Raffle.objects.create(
            name="Test Raffle",
            description="Test Raffle Description",
            creator="Test Creator",
            is_prize_nft=False,
            prize="Test Prize",
            chain=self.chain,
            deadline=timezone.now() + timezone.timedelta(days=1),
            max_number_of_entries=100,
        )

        raffle.permissions.set([self.permission, self.permission2])

    def test_raffle_list(self):
        url = reverse("raffle-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        # check permissions count
        self.assertEqual(len(response.data[0]["permissions"]), 2)
        # check second permission name
        self.assertEqual(
            response.data[0]["permissions"][1]["name"], "BrightID Aura Verification"
        )
