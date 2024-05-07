import datetime
import json
import os
import time
from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from authentication.models import UserProfile, Wallet
from core.models import WalletAccount
from faucet.constants import MEMCACHE_LIGHTNING_LOCK_KEY
from faucet.constraints import OptimismDonationConstraint
from faucet.faucet_manager.claim_manager import ClaimManagerFactory, SimpleClaimManager
from faucet.faucet_manager.credit_strategy import RoundCreditStrategy
from faucet.faucet_manager.fund_manager import LightningFundManager
from faucet.helpers import memcache_lock
from faucet.models import (
    Chain,
    ClaimReceipt,
    DonationReceipt,
    Faucet,
    GlobalSettings,
    LightningConfig,
    NetworkTypes,
    TransactionBatch,
)

address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
fund_manager = "0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0"
faucet1_max_claim = 800e6
faucet2_max_claim = 1000e6
t_chain_max = 500e6

test_rpc_url_private = "http://ganache:7545"
test_wallet_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
test_chain_id = 1337
test_rpc_url = "http://127.0.0.1:7545"

LIGHTNING_WALLET = os.environ.get("LIGHTNING_WALLET")
LIGHTNING_FUND_MANAGER = os.environ.get("LIGHTNING_FUND_MANAGER")

LIGHTNING_RPC_URL = "https://api.lnpay.co/v1/"
LIGHTNING_INVOICE = "lnbc100n1pjxtceppp5q65xc3w8tnnmzkhqgg9c7h4a8hzplm0dppr9\
44upwsq4q62sjeesdqu2askcmr9wssx7e3q2dshgmmndp5scqzzsxqyz5vqsp5hj2vzha0x4qvuyz\
rym6ryvxwnccn4kjwa57037dgcshl5ls4tves9qyyssqj24t4j2dkp2r29ptgxqz2etsk0qp8ggwm\
t20czfu48h5akgme43zevg6x040scjzx3qgtp8mkcg2gurv0hy8d8xm3hhf8k68uefl9sqqqscuvz"


def create_new_user(
    _address="0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9",
) -> UserProfile:
    p = UserProfile.objects.get_or_create(_address)
    return p


def create_test_faucet(
    wallet=None, chain_id=test_chain_id, max_claim_amount=t_chain_max
) -> Faucet:
    if not wallet:
        wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )

    chain = Chain.objects.create(
        chain_name="Ethereum",
        native_currency_name="ethereum",
        symbol="ETH",
        rpc_url_private=test_rpc_url_private,
        wallet=wallet,
        chain_id=chain_id,
        explorer_url="https://ftmscan.com/",
    )
    return Faucet.objects.create(
        chain=chain,
        max_claim_amount=max_claim_amount,
        fund_manager_address=fund_manager,
    )


def create_lightning_faucet(wallet) -> Faucet:
    chain = Chain.objects.create(
        chain_name="Lightning",
        native_currency_name="BTC",
        symbol="BTC",
        rpc_url_private=LIGHTNING_RPC_URL,
        wallet=wallet,
        chain_id=286621,
        explorer_url="https://ftmscan.com/",
    )

    return Faucet.objects.create(
        chain=chain,
        max_claim_amount=100,
        fund_manager_address=LIGHTNING_FUND_MANAGER,
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


class TestChainInfo(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )
        self.new_user = create_new_user()

    def request_chain_list(self):
        endpoint = reverse("FAUCET:faucet-list")
        chains = self.client.get(endpoint)
        return chains

    def test_list_chains(self):
        response = self.request_chain_list()
        self.assertEqual(response.status_code, 200)


class TestClaim(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )
        self.new_user = create_new_user()
        self.verified_user = create_new_user()
        self.test_faucet1 = create_test_faucet(
            self.wallet, max_claim_amount=faucet1_max_claim
        )
        self.test_faucet2 = create_test_faucet(self.wallet, 123, faucet2_max_claim)
        GlobalSettings.set("gastap_round_claim_limit", "2")

    def test_get_claimed_should_be_zero(self):
        credit_strategy_faucet1 = RoundCreditStrategy(self.test_faucet1, self.new_user)
        credit_strategy_faucet2 = RoundCreditStrategy(self.test_faucet2, self.new_user)

        self.assertEqual(credit_strategy_faucet1.get_claimed(), 0)
        self.assertEqual(credit_strategy_faucet2.get_claimed(), 0)
        self.assertEqual(credit_strategy_faucet1.get_unclaimed(), faucet1_max_claim)
        self.assertEqual(credit_strategy_faucet2.get_unclaimed(), faucet2_max_claim)

    def test_x_dai_claimed_be_zero_eth_be_100(self):
        claim_amount = 100
        ClaimReceipt.objects.create(
            faucet=self.test_faucet2,
            user_profile=self.new_user,
            datetime=timezone.now(),
            _status=ClaimReceipt.VERIFIED,
            amount=claim_amount,
        )

        credit_strategy_faucet1 = RoundCreditStrategy(self.test_faucet1, self.new_user)
        credit_strategy_faucet2 = RoundCreditStrategy(self.test_faucet2, self.new_user)

        self.assertEqual(credit_strategy_faucet1.get_claimed(), 0)
        self.assertEqual(credit_strategy_faucet2.get_claimed(), claim_amount)
        self.assertEqual(credit_strategy_faucet1.get_unclaimed(), faucet1_max_claim)
        self.assertEqual(
            credit_strategy_faucet2.get_unclaimed(), faucet2_max_claim - claim_amount
        )

    def test_claim_manager_fail_if_claim_amount_exceeds_unclaimed(self):
        claim_manager_faucet1 = SimpleClaimManager(
            RoundCreditStrategy(self.test_faucet1, self.new_user)
        )

        try:
            claim_manager_faucet1.claim(faucet1_max_claim + 10)
            self.assertEqual(True, False)
        except AssertionError:
            self.assertEqual(True, True)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: False,
    )
    def test_claim_unverified_user_should_fail(self):
        claim_amount = 100
        claim_manager_faucet = SimpleClaimManager(
            RoundCreditStrategy(self.test_faucet1, self.new_user)
        )

        try:
            claim_manager_faucet.claim(claim_amount)
            self.assertEqual(True, False)
        except AssertionError:
            self.assertEqual(True, True)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    def test_claim_manager_should_claim(self):
        claim_amount = 100
        claim_manager_faucet = ClaimManagerFactory(
            self.test_faucet1, self.verified_user
        ).get_manager()
        credit_strategy_faucet = claim_manager_faucet.get_credit_strategy()
        r = claim_manager_faucet.claim(claim_amount, address)
        r._status = ClaimReceipt.VERIFIED
        r.save()

        self.assertEqual(credit_strategy_faucet.get_claimed(), claim_amount)
        self.assertEqual(
            credit_strategy_faucet.get_unclaimed(), faucet1_max_claim - claim_amount
        )

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    def test_only_one_pending_claim(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_faucet = ClaimManagerFactory(
            self.test_faucet1, self.verified_user
        ).get_manager()
        claim_manager_faucet.claim(claim_amount_1, address)

        try:
            claim_manager_faucet.claim(claim_amount_2, address)
        except AssertionError:
            self.assertEqual(True, True)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    def test_second_claim_after_first_verifies(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_faucet = ClaimManagerFactory(
            self.test_faucet1, self.verified_user
        ).get_manager()
        claim_1 = claim_manager_faucet.claim(claim_amount_1, address)
        claim_1._status = ClaimReceipt.VERIFIED
        claim_1.save()
        try:
            claim_manager_faucet.claim(claim_amount_2, address)
        except AssertionError:
            self.assertEqual(False, True)

    @patch(
        "faucet.faucet_manager.claim_manager.SimpleClaimManager.user_is_meet_verified",
        lambda a: True,
    )
    def test_second_claim_after_first_fails(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_faucet = ClaimManagerFactory(
            self.test_faucet1, self.verified_user
        ).get_manager()
        claim_1 = claim_manager_faucet.claim(claim_amount_1, address)
        claim_1._status = ClaimReceipt.REJECTED
        claim_1.save()
        try:
            claim_manager_faucet.claim(claim_amount_2, address)
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
        claim_manager_faucet = ClaimManagerFactory(
            self.test_faucet1, self.verified_user
        ).get_manager()
        claim_1 = claim_manager_faucet.claim(claim_amount_1, address)
        claim_1._status = ClaimReceipt.VERIFIED
        claim_1.save()
        claim_2 = claim_manager_faucet.claim(claim_amount_2, address)
        claim_2._status = ClaimReceipt.VERIFIED
        claim_2.save()

        try:
            claim_manager_faucet.claim(claim_amount_3, address)
        except AssertionError:
            self.assertEqual(True, True)


class TestClaimAPI(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )
        self.lightning_wallet = WalletAccount.objects.create(
            name="Test Lightning Wallet", private_key=LIGHTNING_WALLET
        )
        self.verified_user = create_new_user()
        self.test_faucet = create_test_faucet(self.wallet)
        self.lightning_faucet = create_lightning_faucet(self.lightning_wallet)
        self.initial_context_id = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"

        GlobalSettings.set("gastap_round_claim_limit", "2")
        LightningConfig.objects.create(
            period=86800,
            period_max_cap=100,
            current_round=int(int(time.time()) / 86800) * 86800,
        )

        self.client.force_authenticate(user=self.verified_user.user)
        self.user_profile = self.verified_user

    @patch(
        "authentication.models.UserProfile.is_meet_verified",
        lambda a: (False, None),
    )
    def test_claim_max_api_should_fail_if_not_verified(self):
        endpoint = reverse(
            "FAUCET:claim-max",
            kwargs={"faucet_pk": self.test_faucet.pk},
        )

        response = self.client.post(
            endpoint, data={"address": "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"}
        )
        self.assertEqual(response.status_code, 403)

    @patch(
        "authentication.models.UserProfile.is_meet_verified",
        True,
    )
    def test_claim_max_api_should_claim_all(self):
        endpoint = reverse(
            "FAUCET:claim-max",
            kwargs={"faucet_pk": self.test_faucet.pk},
        )

        response = self.client.post(
            endpoint, data={"address": "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"}
        )
        claim_receipt = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(claim_receipt["amount"], self.test_faucet.max_claim_amount)

    @patch(
        "authentication.models.UserProfile.is_meet_verified",
        True,
    )
    def test_claim_max_twice_should_fail(self):
        endpoint = reverse(
            "FAUCET:claim-max",
            kwargs={"faucet_pk": self.test_faucet.pk},
        )
        response_1 = self.client.post(
            endpoint, data={"address": "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"}
        )
        self.assertEqual(response_1.status_code, 200)
        response_2 = self.client.post(
            endpoint, data={"address": "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"}
        )
        self.assertEqual(response_2.status_code, 403)

    @patch("authentication.models.UserProfile.is_meet_verified", True)
    def test_address_validator_evm(self):
        endpoint = reverse(
            "FAUCET:claim-max", kwargs={"faucet_pk": self.test_faucet.pk}
        )
        response_1 = self.client.post(endpoint, data={"address": "0x132546"})
        self.assertEqual(response_1.status_code, 400)

    def test_get_last_claim_of_user(self):
        endpoint = reverse("FAUCET:last-claim")

        rejected_batch = TransactionBatch.objects.create(
            faucet=self.test_faucet,
            tx_hash="0x1111111111",
            _status=ClaimReceipt.REJECTED,
        )

        ClaimReceipt.objects.create(
            faucet=self.test_faucet,
            batch=rejected_batch,
            amount=1500,
            datetime=timezone.now(),
            _status=ClaimReceipt.REJECTED,
            user_profile=self.user_profile,
        )

        verified_batch = TransactionBatch.objects.create(
            faucet=self.test_faucet,
            tx_hash="0x0000000000",
            _status=ClaimReceipt.VERIFIED,
        )

        last_claim = ClaimReceipt.objects.create(
            faucet=self.test_faucet,
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
        self.assertEqual(claim_data["faucet"]["pk"], last_claim.faucet.pk)

    def test_get_claim_list(self):
        endpoint = reverse("FAUCET:claims")

        rejected_batch = TransactionBatch.objects.create(
            faucet=self.test_faucet,
            tx_hash="0x1111111111",
            _status=ClaimReceipt.REJECTED,
        )

        c1 = ClaimReceipt.objects.create(
            faucet=self.test_faucet,
            batch=rejected_batch,
            amount=1500,
            datetime=timezone.now(),
            _status=ClaimReceipt.REJECTED,
            user_profile=self.user_profile,
        )

        verified_batch = TransactionBatch.objects.create(
            faucet=self.test_faucet,
            tx_hash="0x0000000000",
            _status=ClaimReceipt.VERIFIED,
        )

        c2 = ClaimReceipt.objects.create(
            faucet=self.test_faucet,
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
                invoice = LIGHTNING_INVOICE

                lightning_fund_manager = LightningFundManager(self.lightning_faucet)
                lightning_fund_manager.multi_transfer([{"amount": 10, "data": invoice}])

    def test_lightning_claim_max_cap_exceeded(self):
        lightning_fund_manager = LightningFundManager(self.lightning_faucet)
        config = lightning_fund_manager.config
        config.claimed_amount = 100
        config.save()
        is_exceeded = (
            lightning_fund_manager._LightningFundManager__check_max_cap_exceeds(10)
        )
        self.assertEqual(is_exceeded, True)

        with self.assertRaises(AssertionError):
            invoice = LIGHTNING_INVOICE

            lightning_fund_manager.multi_transfer([{"amount": 10, "data": invoice}])


class TestWeeklyCreditStrategy(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )
        # self.verified_user = create_verified_user()
        self.test_faucet = create_test_faucet(self.wallet)

        self.initial_context_id = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"

        GlobalSettings.set("gastap_round_claim_limit", "2")
        self.user_profile = create_new_user(self._address)
        self.client.force_authenticate(user=self.user_profile.user)

        self.strategy = RoundCreditStrategy(self.test_faucet, self.user_profile)

    def test_last_monday(self):
        now = timezone.now()
        last_monday = RoundCreditStrategy.get_start_of_the_round()
        self.assertGreaterEqual(now, last_monday)

    def create_claim_receipt(self, date, amount=10):
        verified_batch = TransactionBatch.objects.create(
            faucet=self.test_faucet, tx_hash="test-hash", _status=ClaimReceipt.VERIFIED
        )
        ClaimReceipt.objects.create(
            faucet=self.test_faucet,
            user_profile=self.user_profile,
            _status=ClaimReceipt.VERIFIED,
            amount=amount,
            datetime=date,
            batch=verified_batch,
        )

    def test_last_week_claims(self):
        last_monday = RoundCreditStrategy.get_start_of_the_round()
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
        last_monday = RoundCreditStrategy.get_start_of_the_round()
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

        self.test_faucet = create_test_faucet(self.wallet)

        self.optimism_chain = Chain.objects.create(
            chain_name="Optimism",
            native_currency_name="ETH",
            symbol="ETH",
            rpc_url_private="https://optimism.llamarpc.com",
            wallet=self.wallet,
            chain_id=10,
            explorer_url="https://optimistic.etherscan.io/",
            explorer_api_url="https://api-optimistic.etherscan.io",
            explorer_api_key="6PGF5HBTT7DG9CQCQZK3MWR9146JAWQKAC",
        )
        self.optimism_faucet = Faucet.objects.create(
            chain=self.optimism_chain,
            max_claim_amount=t_chain_max,
            fund_manager_address="0xb3A97684Eb67182BAa7994b226e6315196D8b364",
        )

        self.user_profile = create_new_user(
            "0x5A73E32a77E04Fb3285608B0AdEaa000B8e248F2"
        )
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
            user_profile=self.user_profile, tx_hash="0x0", faucet=self.test_faucet
        )
        self.assertFalse(constraint.is_observed())
        DonationReceipt.objects.create(
            user_profile=self.user_profile,
            tx_hash="0x0",
            faucet=self.optimism_faucet,
            status=ClaimReceipt.VERIFIED,
        )
        self.assertTrue(constraint.is_observed())

    # def test_optimism_claiming_gas_contraint(self):
    #     constraint = OptimismClaimingGasConstraint(self.user_profile)
    #     self.assertTrue(constraint.is_observed())
    #     self.wallet.address = "0xE3eEBaB360E367b4e200759F0D955D1140F27430"
    #     self.wallet.save()
    #     self.assertTrue(constraint.is_observed())
    #     self.wallet.address = "0xB9e291b68E584be657477289389B3a6DEED3E34C"
    #     self.wallet.save()
    #     self.assertFalse(constraint.is_observed())


class TestFuelChampion(APITestCase):
    def setUp(self) -> None:
        self.wallet = WalletAccount.objects.create(
            name="Test Wallet", private_key=test_wallet_key
        )

        self.test_faucet = create_test_faucet(self.wallet)

        self.user_profile = create_new_user(
            "0x5A73E32a77E04Fb3285608B0AdEaa000B8e248F4"
        )
        self.wallet = Wallet.objects.create(
            user_profile=self.user_profile,
            wallet_type=NetworkTypes.EVM,
            address="0x5A73E32a77E04Fb3285608B0AdEaa000B8e248F2",
        )
        self.client.force_authenticate(user=self.user_profile.user)

    def tearDown(self) -> None:
        cache.clear()

    def test_get_unverified_fuel_champion(self):
        endpoint = reverse("FAUCET:gas-tap-fuel-champion")
        DonationReceipt.objects.create(
            user_profile=self.user_profile,
            tx_hash="0x0",
            faucet=self.test_faucet,
            value=10,
        )
        res = self.client.get(endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_get_verified_fuel_champion(self):
        endpoint = reverse("FAUCET:gas-tap-fuel-champion")
        DonationReceipt.objects.create(
            user_profile=self.user_profile,
            tx_hash="0x0",
            faucet=self.test_faucet,
            value=10,
            status=ClaimReceipt.VERIFIED,
        )
        res = self.client.get(endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_get_fuel_champion_when_two_person_had_donation(self):
        endpoint = reverse("FAUCET:gas-tap-fuel-champion")
        DonationReceipt.objects.create(
            user_profile=self.user_profile,
            tx_hash="0x0",
            faucet=self.test_faucet,
            value=10,
            status=ClaimReceipt.VERIFIED,
        )
        DonationReceipt.objects.create(
            user_profile=self.user_profile,
            tx_hash="0x1",
            faucet=self.test_faucet,
            value=100,
            status=ClaimReceipt.VERIFIED,
        )
        test_user = create_new_user("0x5A73E32a77E04Fb3285608B0AdEaa000B8e248F3")
        DonationReceipt.objects.create(
            user_profile=test_user,
            tx_hash="0x2",
            faucet=self.test_faucet,
            value=10,
            status=ClaimReceipt.VERIFIED,
        )
        res = self.client.get(endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[-1].get("username", 0), self.user_profile.username)
