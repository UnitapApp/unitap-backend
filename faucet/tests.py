import json
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from faucet.faucet_manager.claim_manager import ClaimManagerFactory
from faucet.faucet_manager.credit_strategy import SimpleCreditStrategy, CreditStrategyFactory
from faucet.models import BrightUser, Chain, ClaimReceipt


def create_new_user() -> BrightUser:
    return BrightUser.get_or_create("0xaa6cD66cA508F22fe125e83342c7dc3dbE779250")


def create_verified_user() -> BrightUser:
    user = create_new_user()
    user._verification_status = BrightUser.VERIFIED
    user.save()
    return user


address = "0xaa6cD66cA508F22fe125e83342c7dc3dbE779250"
x_dai_max_claim = 800
eidi_max_claim = 1000


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

    def test_verify_bright_user(self):
        new_user = create_new_user()
        url = new_user.get_verification_url()
        self.assertEqual(url, "http://<no-link>")
        self.assertEqual(new_user.verification_status, BrightUser.VERIFIED)

    def test_get_verification_url(self):
        endpoint = reverse("FAUCET:get-verification-url",
                           kwargs={'address': address})
        response_1 = self.client.get(endpoint)
        self.assertEqual(response_1.status_code, 200)


def create_xDai_chain():
    return Chain.objects.create(name="Gnosis Chain", symbol="XDAI",
                                chain_id="100", max_claim_amount=x_dai_max_claim)


def create_idChain_chain():
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

    def test_two_claims_after_first_verifies(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_x_dai = ClaimManagerFactory(self.x_dai, self.verified_user).get_manager()
        claim_1 = claim_manager_x_dai.claim(claim_amount_1)
        claim_1._status = ClaimReceipt.VERIFIED
        claim_1.save()
        claim_manager_x_dai.claim(claim_amount_2)

    def test_two_claims_after_first_fails(self):
        claim_amount_1 = 100
        claim_amount_2 = 50
        claim_manager_x_dai = ClaimManagerFactory(self.x_dai, self.verified_user).get_manager()
        claim_1 = claim_manager_x_dai.claim(claim_amount_1)
        claim_1._status = ClaimReceipt.REJECTED
        claim_1.save()
        claim_manager_x_dai.claim(claim_amount_2)
