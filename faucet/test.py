import datetime
import time
import os
import json
from unittest import skipIf
from uuid import uuid4
from django.urls import reverse
from django.utils import timezone
from faucet.views import CustomException
from rest_framework.test import APITestCase
from authentication.models import UserProfile

from brightIDfaucet.settings import DEBUG
from faucet.faucet_manager.claim_manager import ClaimManagerFactory, SimpleClaimManager
from faucet.faucet_manager.credit_strategy import (
    SimpleCreditStrategy,
    WeeklyCreditStrategy,
)

from faucet.faucet_manager.fund_manager import EVMFundManager, LightningFundManager
from faucet.models import (
    Chain,
    ClaimReceipt,
    GlobalSettings,
    WalletAccount,
    TransactionBatch,
    LightningConfig,
    Wallet,
    NetworkTypes
)
from unittest.mock import patch
from dotenv import dotenv_values
from faucet.helpers import memcache_lock
from faucet.constants import *
from faucet.constraints import *

address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
fund_manager = "0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0"
x_dai_max_claim = 800e6
eidi_max_claim = 1000e6
t_chain_max = 500e6

test_rpc_url_private = "http://ganache:7545"
test_wallet_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
test_chain_id = 1337
test_rpc_url = "http://127.0.0.1:7545"

env_config = dotenv_values(".env.test")


def create_new_user(
    _address="0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9",
) -> UserProfile:
    p = UserProfile.objects.get_or_create(_address)
    return p


def create_xDai_chain(wallet) -> Chain:
    return Chain.objects.create(
        chain_name="Gnosis Chain",
        wallet=wallet,
        rpc_url_private=test_rpc_url_private,
        fund_manager_address=fund_manager,
        native_currency_name="xdai",
        symbol="XDAI",
        chain_id="100",
        max_claim_amount=x_dai_max_claim,
        explorer_url="https://ftmscan.com/",
    )


def create_test_chain(wallet) -> Chain:
    return Chain.objects.create(
        chain_name="Ethereum",
        native_currency_name="ethereum",
        symbol="ETH",
        rpc_url_private=test_rpc_url_private,
        wallet=wallet,
        fund_manager_address=fund_manager,
        chain_id=test_chain_id,
        max_claim_amount=t_chain_max,
        explorer_url="https://ftmscan.com/",
    )


def create_idChain_chain(wallet) -> Chain:
    return Chain.objects.create(
        chain_name="IDChain",
        wallet=wallet,
        fund_manager_address=fund_manager,
        native_currency_name="eidi",
        symbol="eidi",
        chain_id="74",
        max_claim_amount=eidi_max_claim,
        explorer_url="https://ftmscan.com/",
    )

def create_lightning_chain(wallet) -> Chain:
    return Chain.objects.create(
        chain_name="Lightning",
        native_currency_name="BTC",
        symbol="BTC",
        rpc_url_private=env_config['LIGHTNING_RPC_URL'],
        wallet=wallet,
        fund_manager_address=env_config['LIGHTNING_FUND_MANAGER'],
        chain_id=286621,
        max_claim_amount=10,
        explorer_url="https://ftmscan.com/",
    )


class TestWalletAccount(APITestCase):
    def setUp(self) -> None:
        self.key = test_wallet_key
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )

    def test_create_wallet(self):
        self.assertEqual(WalletAccount.objects.count(), 1)
        self.assertEqual(self.wallet.main_key, self.key)
        self.assertEqual(WalletAccount.objects.first(), self.wallet)


# class TestCreateAccount(APITestCase):
#     @bright_interface_mock
#     def test_create_bright_user(self):
#         endpoint = reverse("FAUCET:create-user")
#         response = self.client.post(endpoint, data={"address": address})
#         self.assertEqual(response.status_code, 201)
#         self.assertIsNotNone(json.loads(response.content).get("contextId"))
#         self.assertEqual(json.loads(response.content).get("address"), address)
#
#     @bright_interface_mock
#     def test_get_user_info(self):
#         user = create_new_user()
#         endpoint = reverse("FAUCET:user-info", kwargs={"address": user.address})
#         response = self.client.get(endpoint)
#
#         self.assertEqual(response.status_code, 200)
#
#     @bright_interface_mock
#     def test_should_fail_to_create_duplicate_address(self):
#         endpoint = reverse("FAUCET:create-user")
#         response_1 = self.client.post(endpoint, data={"address": address})
#         response_2 = self.client.post(endpoint, data={"address": address})
#
#         self.assertEqual(response_1.status_code, 201)
#         self.assertEqual(response_2.status_code, 400)
#
#     @bright_interface_mock
#     def test_newly_created_user_verification_status_should_be_pending(self):
#         new_user = create_new_user()
#         self.assertEqual(new_user.verification_status, ClaimReceipt.PENDING)
#
#     @bright_interface_mock
#     def test_newly_created_user_verification_status_should_be_pending(self):
#         new_user = create_new_user()
#         self.assertEqual(new_user.verification_status, ClaimReceipt.PENDING)

# @bright_interface_mock(status_mock=True)
# def test_verify_bright_user(self):
#     print("\n\n\n\n\n\nbefore creating user\n\n\n\n\n\n\n")
#     new_user = create_new_user()
#     print("\n\n\n\n\n\nafter creating user\n\n\n\n\n\n")
#     url = new_user.get_verification_url()
#     print("\n\n\n\n\n\nafter getting verification\n\n\n\n\n\n")
#     self.assertEqual(url, "http://<no-link>")
#     self.assertEqual(new_user.verification_status, ClaimReceipt.VERIFIED)
#
# @bright_interface_mock
# def test_get_verification_url(self):
#     endpoint = reverse("FAUCET:get-verification-url", kwargs={"address": address})
#     response_1 = self.client.get(endpoint)
#     self.assertEqual(response_1.status_code, 200)
#     self.assertAlmostEqual(response_1.json()["verificationUrl"], "http://<no-link>")


class TestChainInfo(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )
        self.new_user = create_new_user()
        self.xdai = create_xDai_chain(self.wallet)
        self.idChain = create_idChain_chain(self.wallet)

    def request_chain_list(self):
        endpoint = reverse("FAUCET:chain-list")
        chains = self.client.get(endpoint)
        return chains

    def test_list_chains(self):
        response = self.request_chain_list()
        self.assertEqual(response.status_code, 200)

    def test_list_chain_should_show_NA_if_no_addresses_provided(self):
        chains = self.request_chain_list()
        chains_list = json.loads(chains.content)

        for chain_data in chains_list:
            self.assertEqual(chain_data["claimed"], "N/A")
            self.assertEqual(chain_data["unclaimed"], "N/A")
            if chain_data["symbol"] == "XDAI":
                self.assertEqual(chain_data["maxClaimAmount"], x_dai_max_claim)
            elif chain_data["symbol"] == "eidi":
                self.assertEqual(chain_data["maxClaimAmount"], eidi_max_claim)

    def test_chain_list_without_token(self):
        endpoint = reverse("FAUCET:chain-list")
        chain_list_response = self.client.get(endpoint)
        chain_list = json.loads(chain_list_response.content)

        for chain_data in chain_list:
            self.assertEqual(chain_data["claimed"], "N/A")
            self.assertEqual(chain_data["unclaimed"], "N/A")

    def test_chain_list_with_token(self):
        endpoint = reverse("FAUCET:chain-list")
        self.client.force_authenticate(user=self.new_user.user)
        chain_list_response = self.client.get(endpoint)
        chain_list = json.loads(chain_list_response.content)

        for chain_data in chain_list:
            self.assertEqual(chain_data["claimed"], 0)
            self.assertEqual(chain_data["unclaimed"], chain_data["maxClaimAmount"])


class TestClaim(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )
        self.new_user = create_new_user()
        self.verified_user = create_new_user()
        self.x_dai = create_xDai_chain(self.wallet)
        self.idChain = create_idChain_chain(self.wallet)
        self.test_chain = create_test_chain(self.wallet)
        GlobalSettings.objects.create(weekly_chain_claim_limit=2)

    def test_get_claimed_should_be_zero(self):
        credit_strategy_xdai = WeeklyCreditStrategy(self.x_dai, self.new_user)
        credit_strategy_id_chain = WeeklyCreditStrategy(self.idChain, self.new_user)

        self.assertEqual(credit_strategy_xdai.get_claimed(), 0)
        self.assertEqual(credit_strategy_id_chain.get_claimed(), 0)
        self.assertEqual(credit_strategy_xdai.get_unclaimed(), x_dai_max_claim)
        self.assertEqual(credit_strategy_id_chain.get_unclaimed(), eidi_max_claim)

    def test_x_dai_claimed_be_zero_eth_be_100(self):
        claim_amount = 100
        ClaimReceipt.objects.create(
            chain=self.idChain,
            user_profile=self.new_user,
            datetime=timezone.now(),
            _status=ClaimReceipt.VERIFIED,
            amount=claim_amount,
        )

        credit_strategy_xdai = WeeklyCreditStrategy(self.x_dai, self.new_user)
        credit_strategy_id_chain = WeeklyCreditStrategy(self.idChain, self.new_user)

        self.assertEqual(credit_strategy_xdai.get_claimed(), 0)
        self.assertEqual(credit_strategy_id_chain.get_claimed(), claim_amount)
        self.assertEqual(credit_strategy_xdai.get_unclaimed(), x_dai_max_claim)
        self.assertEqual(
            credit_strategy_id_chain.get_unclaimed(), eidi_max_claim - claim_amount
        )

    def test_claim_manager_fail_if_claim_amount_exceeds_unclaimed(self):
        claim_manager_x_dai = SimpleClaimManager(
            WeeklyCreditStrategy(self.x_dai, self.new_user)
        )

        try:
            claim_manager_x_dai.claim(x_dai_max_claim + 10)
            self.assertEqual(True, False)
        except AssertionError:
            self.assertEqual(True, True)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: False,
    )
    def test_claim_unverified_user_should_fail(self):
        claim_amount = 100
        claim_manager_x_dai = SimpleClaimManager(
            WeeklyCreditStrategy(self.x_dai, self.new_user)
        )

        try:
            claim_manager_x_dai.claim(claim_amount)
            self.assertEqual(True, False)
        except AssertionError:
            self.assertEqual(True, True)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    def test_claim_manager_should_claim(self):
        claim_amount = 100
        claim_manager_x_dai = ClaimManagerFactory(
            self.x_dai, self.verified_user
        ).get_manager()
        credit_strategy_x_dai = claim_manager_x_dai.get_credit_strategy()
        r = claim_manager_x_dai.claim(claim_amount)
        r._status = ClaimReceipt.VERIFIED
        r.save()

        self.assertEqual(credit_strategy_x_dai.get_claimed(), claim_amount)
        self.assertEqual(
            credit_strategy_x_dai.get_unclaimed(), x_dai_max_claim - claim_amount
        )

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    def test_only_one_pending_claim(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_x_dai = ClaimManagerFactory(
            self.x_dai, self.verified_user
        ).get_manager()
        claim_manager_x_dai.claim(claim_amount_1)

        try:
            claim_manager_x_dai.claim(claim_amount_2)
        except AssertionError:
            self.assertEqual(True, True)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    def test_second_claim_after_first_verifies(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_x_dai = ClaimManagerFactory(
            self.x_dai, self.verified_user
        ).get_manager()
        claim_1 = claim_manager_x_dai.claim(claim_amount_1)
        claim_1._status = ClaimReceipt.VERIFIED
        claim_1.save()
        try:
            claim_manager_x_dai.claim(claim_amount_2)
        except AssertionError:
            self.assertEqual(False, True)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    def test_second_claim_after_first_fails(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_x_dai = ClaimManagerFactory(
            self.x_dai, self.verified_user
        ).get_manager()
        claim_1 = claim_manager_x_dai.claim(claim_amount_1)
        claim_1._status = ClaimReceipt.REJECTED
        claim_1.save()
        try:
            claim_manager_x_dai.claim(claim_amount_2)
        except AssertionError:
            self.assertEqual(True, False)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    def test_claim_should_fail_if_limit_reached(self):
        claim_amount_1 = 10
        claim_amount_2 = 5
        claim_amount_3 = 1
        claim_manager_x_dai = ClaimManagerFactory(
            self.x_dai, self.verified_user
        ).get_manager()
        claim_1 = claim_manager_x_dai.claim(claim_amount_1)
        claim_1._status = ClaimReceipt.VERIFIED
        claim_1.save()
        claim_2 = claim_manager_x_dai.claim(claim_amount_2)
        claim_2._status = ClaimReceipt.VERIFIED
        claim_2.save()

        try:
            claim_manager_x_dai.claim(claim_amount_3)
        except AssertionError:
            self.assertEqual(True, True)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    @skipIf(not DEBUG, "only on debug")
    def test_simple_claim_manager_transfer(self):
        manager = SimpleClaimManager(
            SimpleCreditStrategy(self.test_chain, self.verified_user)
        )
        manager.claim(100)


class TestClaimAPI(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )
        self.lightning_wallet = WalletAccount.objects.create(
            name="Test Lightning Wallet", private_key=env_config['LIGHTNING_WALLET']
        )
        self.verified_user = create_new_user()
        self.x_dai = create_xDai_chain(self.wallet)
        self.idChain = create_idChain_chain(self.wallet)
        self.test_chain = create_test_chain(self.wallet)
        self.lightning_chain = create_lightning_chain(self.lightning_wallet)
        self.initial_context_id = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"

        GlobalSettings.objects.create(weekly_chain_claim_limit=2)
        LightningConfig.objects.create(
            period=86800,
            period_max_cap=100,
            current_round=int(int(time.time()) / 86800) * 86800
        )

        self.client.force_authenticate(user=self.verified_user.user)
        self.user_profile = self.verified_user

    @patch("faucet.views.ClaimMaxView.wallet_address_is_set", lambda a: (True, None))
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (False, None),
    )
    def test_claim_max_api_should_fail_if_not_verified(self):
        endpoint = reverse(
            "FAUCET:claim-max",
            kwargs={"chain_pk": self.x_dai.pk},
        )

        response = self.client.post(endpoint)
        self.assertEqual(response.status_code, 403)

    @patch("faucet.views.ClaimMaxView.wallet_address_is_set", lambda a: (True, None))
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_claim_max_api_should_claim_all(self):
        endpoint = reverse(
            "FAUCET:claim-max",
            kwargs={"chain_pk": self.x_dai.pk},
        )

        response = self.client.post(endpoint)
        claim_receipt = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(claim_receipt["amount"], self.x_dai.max_claim_amount)

    @patch("faucet.views.ClaimMaxView.wallet_address_is_set", lambda a: (True, None))
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_claim_max_twice_should_fail(self):
        endpoint = reverse(
            "FAUCET:claim-max",
            kwargs={"chain_pk": self.x_dai.pk},
        )
        response_1 = self.client.post(endpoint)
        self.assertEqual(response_1.status_code, 200)
        try:
            self.client.post(endpoint)
        except CustomException:
            self.assertEqual(True, True)

    @patch("faucet.views.ClaimMaxView.wallet_address_is_set", lambda a: (True, None))
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_get_last_claim_of_user(self):

        endpoint = reverse("FAUCET:last-claim")

        rejected_batch = TransactionBatch.objects.create(
            chain=self.test_chain, tx_hash="0x1111111111", _status=ClaimReceipt.REJECTED
        )

        ClaimReceipt.objects.create(
            chain=self.test_chain,
            batch=rejected_batch,
            amount=1500,
            datetime=timezone.now(),
            _status=ClaimReceipt.REJECTED,
            user_profile=self.user_profile,
        )

        verified_batch = TransactionBatch.objects.create(
            chain=self.test_chain, tx_hash="0x0000000000", _status=ClaimReceipt.VERIFIED
        )

        last_claim = ClaimReceipt.objects.create(
            chain=self.test_chain,
            batch=verified_batch,
            amount=1000,
            datetime=timezone.now(),
            _status=ClaimReceipt.VERIFIED,
            user_profile=self.user_profile,
        )

        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, 200)
        claim_data = json.loads(response.content)

        self.assertEqual(claim_data["pk"], last_claim.pk)
        self.assertEqual(claim_data["status"], last_claim._status)
        self.assertEqual(claim_data["txHash"], last_claim.tx_hash)
        self.assertEqual(claim_data["chain"]["pk"], last_claim.chain.pk)

    @patch("faucet.views.ClaimMaxView.wallet_address_is_set", lambda a: (True, None))
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_get_claim_list(self):
        endpoint = reverse("FAUCET:claims")

        rejected_batch = TransactionBatch.objects.create(
            chain=self.test_chain, tx_hash="0x1111111111", _status=ClaimReceipt.REJECTED
        )

        c1 = ClaimReceipt.objects.create(
            chain=self.test_chain,
            batch=rejected_batch,
            amount=1500,
            datetime=timezone.now(),
            _status=ClaimReceipt.REJECTED,
            user_profile=self.user_profile,
        )

        verified_batch = TransactionBatch.objects.create(
            chain=self.test_chain, tx_hash="0x0000000000", _status=ClaimReceipt.VERIFIED
        )

        c2 = ClaimReceipt.objects.create(
            chain=self.test_chain,
            batch=verified_batch,
            amount=1000,
            datetime=timezone.now(),
            _status=ClaimReceipt.VERIFIED,
            user_profile=self.user_profile,
        )

        response = self.client.get(endpoint)
        data = json.loads(response.content)
        self.assertEqual(data[0]["pk"], c2.pk)
        self.assertEqual(data[1]["pk"], c1.pk)

    def test_lightning_claim_race_condition(self):
        with self.assertRaises(AssertionError):
            with memcache_lock(MEMCACHE_LIGHTNING_LOCK_KEY, os.getpid()):
                invoice = env_config['LIGHTNING_INVOICE']

                lightning_fund_manager = LightningFundManager(self.lightning_chain)
                lightning_fund_manager.multi_transfer([{
                    "amount": 10,
                    "data": invoice
                }])

    def test_lightning_claim_max_cap_exceeded(self):
        lightning_fund_manager = LightningFundManager(self.lightning_chain)
        config = lightning_fund_manager.config
        config.claimed_amount = 100
        config.save()
        is_exceeded = lightning_fund_manager._LightningFundManager__check_max_cap_exceeds(10)
        self.assertEqual(is_exceeded, True)

        with self.assertRaises(AssertionError):
            invoice = env_config['LIGHTNING_INVOICE']

            lightning_fund_manager.multi_transfer([{
                "amount": 10,
                "data": invoice
            }])



class TestWeeklyCreditStrategy(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )
        # self.verified_user = create_verified_user()
        self.test_chain = create_test_chain(self.wallet)

        self.initial_context_id = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"

        GlobalSettings.objects.create(weekly_chain_claim_limit=2)
        self.user_profile = create_new_user(self._address)
        self.client.force_authenticate(user=self.user_profile.user)

        self.strategy = WeeklyCreditStrategy(self.test_chain, self.user_profile)

    def test_last_monday(self):
        now = timezone.now()
        last_monday = WeeklyCreditStrategy.get_last_monday()
        self.assertGreaterEqual(now, last_monday)

    def create_claim_receipt(self, date, amount=10):
        verified_batch = TransactionBatch.objects.create(
            chain=self.test_chain, tx_hash="test-hash", _status=ClaimReceipt.VERIFIED
        )
        ClaimReceipt.objects.create(
            chain=self.test_chain,
            user_profile=self.user_profile,
            _status=ClaimReceipt.VERIFIED,
            amount=amount,
            datetime=date,
            batch=verified_batch,
        )

    def test_last_week_claims(self):
        last_monday = WeeklyCreditStrategy.get_last_monday()
        last_sunday = last_monday - datetime.timedelta(days=1)
        tuesday = last_monday + datetime.timedelta(days=1)
        wednesday = last_monday + datetime.timedelta(days=2)

        # last sunday
        self.create_claim_receipt(last_sunday)
        self.create_claim_receipt(last_monday)
        self.create_claim_receipt(tuesday)
        self.create_claim_receipt(wednesday)

        total_claimed = self.strategy.get_claimed()
        self.assertEqual(total_claimed, 30)

    def test_unclaimed(self):
        last_monday = WeeklyCreditStrategy.get_last_monday()
        last_sunday = last_monday - datetime.timedelta(days=1)
        tuesday = last_monday + datetime.timedelta(days=1)

        self.create_claim_receipt(date=last_sunday, amount=t_chain_max)
        self.create_claim_receipt(tuesday, 100)

        unclaimed = self.strategy.get_unclaimed()
        self.assertEqual(unclaimed, t_chain_max - 100)


class TestConstraints(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )

        self.test_chain = create_test_chain(self.wallet)

        self.optimism = Chain.objects.create(
            chain_name="Optimism",
            native_currency_name="ETH",
            symbol="ETH",
            rpc_url_private="https://optimism.llamarpc.com",
            wallet=self.wallet,
            fund_manager_address="0xb3A97684Eb67182BAa7994b226e6315196D8b364",
            chain_id=10,
            max_claim_amount=t_chain_max,
            explorer_url="https://optimistic.etherscan.io/",
            explorer_api_url = "https://api-optimistic.etherscan.io",
            explorer_api_key = "6PGF5HBTT7DG9CQCQZK3MWR9146JAWQKAC"
        )

        self.user_profile = create_new_user("0x5A73E32a77E04Fb3285608B0AdEaa000B8e248F2")
        self.wallet = Wallet.objects.create(
            user_profile=self.user_profile,
            wallet_type=NetworkTypes.EVM,
            address="0x5A73E32a77E04Fb3285608B0AdEaa000B8e248F2",
        )
        self.client.force_authenticate(user=self.user_profile.user)

    def test_optimism_donation_contraint(self):
        constraint = OptimismDonationConstraint(self.user_profile)
        self.assertFalse(constraint.is_observed())
        DonationReceipt.objects.create(
            user_profile=self.user_profile,
            tx_hash = "0x0",
            chain = self.test_chain   
        )
        self.assertFalse(constraint.is_observed())
        DonationReceipt.objects.create(
            user_profile=self.user_profile,
            tx_hash = "0x0",
            chain = self.optimism   
        )
        self.assertTrue(constraint.is_observed())

    def test_optimism_claiming_gas_contraint(self):
        constraint = OptimismClaimingGasConstraint(self.user_profile)
        self.assertTrue(constraint.is_observed())
        self.wallet.address = "0xE3eEBaB360E367b4e200759F0D955D1140F27430"
        self.wallet.save()
        self.assertTrue(constraint.is_observed())
        self.wallet.address = "0xB9e291b68E584be657477289389B3a6DEED3E34C"
        self.wallet.save()
        self.assertFalse(constraint.is_observed())
