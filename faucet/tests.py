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
        self.new_user = self.create_new_user()

    @staticmethod
    def create_new_user():
        _uuid = uuid.uuid4()
        user = User.objects.create_user(username=str(_uuid))
        return BrightUser.objects.create(user=user, context_id=_uuid)

    def test_create_bright_user(self):
        endpoint = reverse("FAUCET:create-user")
        response = self.client.post(endpoint)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(json.loads(response.content).get('context_id'))

    def test_newly_created_user_verification_status_should_be_pending(self):
        self.assertEqual(self.new_user.get_verification_status(self.mock_bright_id_driver), BrightUser.PENDING)

    def test_verify_bright_user(self):
        url = self.new_user.get_verification_url(self.mock_bright_id_driver)
        self.assertEqual(url, "http://<no-link>")
        self.assertEqual(self.new_user.get_verification_status(self.mock_bright_id_driver), BrightUser.VERIFIED)
