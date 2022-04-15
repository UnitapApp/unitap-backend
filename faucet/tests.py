import json
import uuid
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from brightIDfaucet.settings import APP_NAME
from faucet.brightID_driver import BrightIDDeriver
from faucet.models import BrightUser


class MockBrightIdDriver(BrightIDDeriver):
    states = {}

    def __init__(self, app_name):
        super(MockBrightIdDriver, self).__init__(app_name)

    def get_verification_link(self, context_id, network="app"):
        self.states[context_id] = True
        return "http://<no-link>"

    def get_verification_status(self, context_id, network="node"):
        return self.states.get(context_id, False)


class TestCreateAccount(APITestCase):

    def setUp(self) -> None:
        self.mock_bright_id_driver = MockBrightIdDriver(APP_NAME)

    @staticmethod
    def create_new_user():
        return BrightUser.get_or_create("0xaa6cD66cA508F22fe125e83342c7dc3dbE779250")

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
        new_user = self.create_new_user()
        self.assertEqual(new_user.get_verification_status(self.mock_bright_id_driver), BrightUser.PENDING)

    def test_verify_bright_user(self):
        new_user = self.create_new_user()
        url = new_user.get_verification_url(self.mock_bright_id_driver)
        self.assertEqual(url, "http://<no-link>")
        self.assertEqual(new_user.get_verification_status(self.mock_bright_id_driver), BrightUser.VERIFIED)

    def test_get_verification_url(self):
        endpoint = reverse("FAUCET:get-verification-url",
                           kwargs={'address': "0xaa6cD66cA508F22fe125e83342c7dc3dbE779250"})
        response_1 = self.client.get(endpoint)
        self.assertEqual(response_1.status_code, 200)
