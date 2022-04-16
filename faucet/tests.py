import json
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from faucet.faucet_manager.credit_strategy import SimpleCreditStrategy, CreditStrategyFactory
from faucet.models import BrightUser, Chain, ClaimReceipt


def create_new_user():
    return BrightUser.get_or_create("0xaa6cD66cA508F22fe125e83342c7dc3dbE779250")


class TestCreateAccount(APITestCase):

    def test_create_bright_user(self):
        endpoint = reverse("FAUCET:create-user")
        response = self.client.post(endpoint, data={
            'address': "0xaa6cD66cA508F22fe125e83342c7dc3dbE779250"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(json.loads(response.content).get('context_id'))
        self.assertEqual(json.loads(response.content).get('address'), "0xaa6cD66cA508F22fe125e83342c7dc3dbE779250")

    def test_should_fail_to_create_duplicate_address(self):
        endpoint = reverse("FAUCET:create-user")
        response_1 = self.client.post(endpoint, data={
            'address': "0xaa6cD66cA508F22fe125e83342c7dc3dbE779250"
        })
        response_2 = self.client.post(endpoint, data={
            'address': "0xaa6cD66cA508F22fe125e83342c7dc3dbE779250"
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
                           kwargs={'address': "0xaa6cD66cA508F22fe125e83342c7dc3dbE779250"})
        response_1 = self.client.get(endpoint)
        self.assertEqual(response_1.status_code, 200)


class TestChainInfo(APITestCase):

    def test_list_chains(self):
        endpoint = reverse("FAUCET:chain-list")
        chains = self.client.get(endpoint)
        self.assertEqual(chains.status_code, 200)


def create_xDai_chain():
    return Chain.objects.create(name="Gnosis Chain", symbol="XDAI",
                                chain_id="100", max_claim_amount=800)


def create_idChain_chain():
    return Chain.objects.create(name="IDChain", symbol="eidi", chain_id="74", max_claim_amount=1000)


class TestClaim(APITestCase):

    def setUp(self) -> None:
        self.new_user = create_new_user()
        self.xdai = create_xDai_chain()
        self.idChain = create_idChain_chain()

    def test_get_claimed_should_be_zero(self):
        credit_strategy_xdai = CreditStrategyFactory(self.xdai, self.new_user).get_strategy()
        credit_strategy_idChain = CreditStrategyFactory(self.idChain, self.new_user).get_strategy()

        self.assertEqual(credit_strategy_xdai.get_claimed(), 0)
        self.assertEqual(credit_strategy_idChain.get_claimed(), 0)
        self.assertEqual(credit_strategy_xdai.get_unclaimed(), 800)
        self.assertEqual(credit_strategy_idChain.get_unclaimed(), 1000)

    def test_xdai_claimed_be_zero_eth_be_100(self):
        ClaimReceipt.objects.create(chain=self.idChain,
                                    bright_user=self.new_user,
                                    datetime=timezone.now(),
                                    amount=100)

        credit_strategy_xdai = CreditStrategyFactory(self.xdai, self.new_user).get_strategy()
        credit_strategy_idChain = CreditStrategyFactory(self.idChain, self.new_user).get_strategy()
        self.assertEqual(credit_strategy_xdai.get_claimed(), 0)
        self.assertEqual(credit_strategy_idChain.get_claimed(), 100)
        self.assertEqual(credit_strategy_xdai.get_unclaimed(), 800)
        self.assertEqual(credit_strategy_idChain.get_unclaimed(), 900)
