import json
from unittest import skipIf

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from brightIDfaucet.private import DEBUG
from brightIDfaucet.settings import BRIGHT_ID_INTERFACE
from faucet.faucet_manager.claim_manager import ClaimManager, ClaimManagerFactory, SimpleClaimManager
from faucet.faucet_manager.credit_strategy import CreditStrategyFactory, SimpleCreditStrategy
from faucet.models import BrightUser, Chain, ClaimReceipt


def create_new_user(_address="0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9") -> BrightUser:
    return BrightUser.get_or_create(_address)


def create_verified_user() -> BrightUser:
    user = create_new_user("0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e")
    user._verification_status = BrightUser.VERIFIED
    user.save()
    return user


address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
x_dai_max_claim = 800
eidi_max_claim = 1000
t_chain_max = 500


class TestCreateAccount(APITestCase):

    def test_create_bright_user(self):
        endpoint = reverse("FAUCET:create-user")
        response = self.client.post(endpoint, data={
            'address': address
        })
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(json.loads(response.content).get('context_id'))
        self.assertEqual(json.loads(response.content).get('address'), address)

    def test_should_fail_to_create_duplicate_address(self):
        endpoint = reverse("FAUCET:create-user")
        response_1 = self.client.post(endpoint, data={
            'address': address
        })
        response_2 = self.client.post(endpoint, data={
            'address': address
        })

        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_2.status_code, 400)

    def test_newly_created_user_verification_status_should_be_pending(self):
        new_user = create_new_user()
        self.assertEqual(new_user.verification_status, BrightUser.PENDING)

    @skipIf(not DEBUG, "Only On Debug")
    def test_verify_bright_user(self):
        new_user = create_new_user()
        url = new_user.get_verification_url()
        BRIGHT_ID_INTERFACE.verify(str(new_user.context_id))
        self.assertEqual(url, "http://<no-link>")
        self.assertEqual(new_user.verification_status, BrightUser.VERIFIED)

    def test_get_verification_url(self):
        endpoint = reverse("FAUCET:get-verification-url",
                           kwargs={'address': address})
        response_1 = self.client.get(endpoint)
        self.assertEqual(response_1.status_code, 200)


def create_xDai_chain() -> Chain:
    return Chain.objects.create(name="Gnosis Chain", symbol="XDAI",
                                chain_id="100", max_claim_amount=x_dai_max_claim)


def create_test_chain() -> Chain:
    return Chain.objects.create(name="Ethereum", symbol="ETH", rpc_url="http://127.0.0.1:7545",
                                wallet_key="0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d",
                                chain_id="1337", max_claim_amount=t_chain_max)


def create_idChain_chain() -> Chain:
    return Chain.objects.create(name="IDChain", symbol="eidi", chain_id="74", max_claim_amount=eidi_max_claim)


class TestChainInfo(APITestCase):
    def setUp(self) -> None:
        self.new_user = create_new_user()
        self.xdai = create_xDai_chain()
        self.idChain = create_idChain_chain()

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
            self.assertEqual(chain_data['claimed'], "N/A")
            self.assertEqual(chain_data['unclaimed'], 'N/A')
            if chain_data['symbol'] == "XDAI":
                self.assertEqual(chain_data['max_claim_amount'], x_dai_max_claim)
            elif chain_data['symbol'] == "eidi":
                self.assertEqual(chain_data['max_claim_amount'], eidi_max_claim)

    def test_chain_list_with_address(self):
        endpoint = reverse("FAUCET:chain-list-address", kwargs={'address': address})
        chain_list_response = self.client.get(endpoint)
        chain_list = json.loads(chain_list_response.content)

        for chain_data in chain_list:
            self.assertEqual(chain_data['claimed'], 0)
            self.assertEqual(chain_data['unclaimed'], chain_data['max_claim_amount'])


class TestClaim(APITestCase):

    def setUp(self) -> None:
        self.new_user = create_new_user()
        self.verified_user = create_verified_user()
        self.x_dai = create_xDai_chain()
        self.idChain = create_idChain_chain()
        self.test_chain = create_test_chain()

    def test_get_claimed_should_be_zero(self):
        credit_strategy_xdai = CreditStrategyFactory(self.x_dai, self.new_user).get_strategy()
        credit_strategy_id_chain = CreditStrategyFactory(self.idChain, self.new_user).get_strategy()

        self.assertEqual(credit_strategy_xdai.get_claimed(), 0)
        self.assertEqual(credit_strategy_id_chain.get_claimed(), 0)
        self.assertEqual(credit_strategy_xdai.get_unclaimed(), x_dai_max_claim)
        self.assertEqual(credit_strategy_id_chain.get_unclaimed(), eidi_max_claim)

    def test_x_dai_claimed_be_zero_eth_be_100(self):
        claim_amount = 100
        ClaimReceipt.objects.create(chain=self.idChain,
                                    bright_user=self.new_user,
                                    datetime=timezone.now(),
                                    amount=claim_amount)

        credit_strategy_xdai = CreditStrategyFactory(self.x_dai, self.new_user).get_strategy()
        credit_strategy_id_chain = CreditStrategyFactory(self.idChain, self.new_user).get_strategy()
        self.assertEqual(credit_strategy_xdai.get_claimed(), 0)
        self.assertEqual(credit_strategy_id_chain.get_claimed(), claim_amount)
        self.assertEqual(credit_strategy_xdai.get_unclaimed(), x_dai_max_claim)
        self.assertEqual(credit_strategy_id_chain.get_unclaimed(), eidi_max_claim - claim_amount)

    def test_claim_manager_fail_if_claim_amount_exceeds_unclaimed(self):
        claim_manager_x_dai = ClaimManagerFactory(self.x_dai, self.new_user).get_manager()
        try:
            claim_manager_x_dai.claim(x_dai_max_claim + 10)
            self.assertEqual(True, False)
        except AssertionError:
            self.assertEqual(True, True)

    def test_claim_unverified_user_should_fail(self):
        claim_amount = 100
        claim_manager_x_dai = ClaimManagerFactory(self.x_dai, self.new_user).get_manager()

        try:
            claim_manager_x_dai.claim(claim_amount)
            self.assertEqual(True, False)
        except AssertionError:
            self.assertEqual(True, True)

    def test_claim_manager_should_claim(self):
        claim_amount = 100
        claim_manager_x_dai = ClaimManagerFactory(self.x_dai, self.verified_user).get_manager()
        credit_strategy_x_dai = CreditStrategyFactory(self.x_dai, self.verified_user).get_strategy()

        claim_manager_x_dai.claim(claim_amount)

        self.assertEqual(credit_strategy_x_dai.get_claimed(), claim_amount)
        self.assertEqual(credit_strategy_x_dai.get_unclaimed(), x_dai_max_claim - claim_amount)

    def test_only_one_pending_claim(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_x_dai = ClaimManagerFactory(self.x_dai, self.verified_user).get_manager()
        claim_manager_x_dai.claim(claim_amount_1)

        try:
            claim_manager_x_dai.claim(claim_amount_2)
            self.assertEqual(True, False)
        except AssertionError:
            self.assertEqual(True, True)

    def test_second_claim_after_first_verifies(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_x_dai = ClaimManagerFactory(self.x_dai, self.verified_user).get_manager()
        claim_1 = claim_manager_x_dai.claim(claim_amount_1)
        claim_1._status = ClaimReceipt.VERIFIED
        claim_1.save()
        claim_manager_x_dai.claim(claim_amount_2)

    def test_second_claim_after_first_fails(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_x_dai = ClaimManagerFactory(self.x_dai, self.verified_user).get_manager()
        claim_1 = claim_manager_x_dai.claim(claim_amount_1)
        claim_1._status = ClaimReceipt.REJECTED
        claim_1.save()
        claim_manager_x_dai.claim(claim_amount_2)

    def test_transfer(self):
        receipt = self.test_chain.transfer(self.verified_user, 100)
        self.assertEqual(receipt.amount, 100)

    def test_simple_claim_manager_transfer(self):
        manager = SimpleClaimManager(SimpleCreditStrategy(self.test_chain, self.verified_user))
        receipt = manager.claim(100)
        self.assertEqual(receipt.amount, 100)


class TestClaimAPI(APITestCase):
    def setUp(self) -> None:
        self.new_user = create_new_user()
        self.verified_user = create_verified_user()
        self.x_dai = create_xDai_chain()
        self.idChain = create_idChain_chain()
        self.test_chain = create_test_chain()

    def test_claim_max_api_should_fail_if_not_verified(self):
        endpoint = reverse("FAUCET:claim-max", kwargs={'address': self.new_user.address,
                                                       'chain_pk': self.x_dai.pk})
        response = self.client.post(endpoint)

        self.assertEqual(response.status_code, 406)

    def test_claim_max_api_should_claim_all(self):
        endpoint = reverse("FAUCET:claim-max", kwargs={'address': self.verified_user.address,
                                                       'chain_pk': self.x_dai.pk})

        response = self.client.post(endpoint)
        claim_receipt = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(claim_receipt['amount'], self.x_dai.max_claim_amount)

    def test_claim_max_twice_should_fail(self):
        endpoint = reverse("FAUCET:claim-max", kwargs={'address': self.verified_user.address,
                                                       'chain_pk': self.x_dai.pk})
        response_1 = self.client.post(endpoint)
        self.assertEqual(response_1.status_code, 200)

        response_2 = self.client.post(endpoint)
        self.assertEqual(response_2.status_code, 403)
