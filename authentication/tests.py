from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
)
from rest_framework.test import APITestCase

from authentication.models import UserProfile, Wallet
from faucet.models import ClaimReceipt

# get address as username and signed address as password and verify signature

# retrieve address from brightID

address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
fund_manager = "0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0"
x_dai_max_claim = 800e6
eidi_max_claim = 1000e6
t_chain_max = 500e6

test_rpc_url_private = "http://ganache:7545"
test_wallet_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
test_chain_id = 1337
test_rpc_url = "http://127.0.0.1:7545"


@patch(
    "faucet.faucet_manager.bright_id_interface.BrightIDInterface.sponsor",
    lambda a, b: True,
)
def create_new_user(
    _address="0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9",
) -> UserProfile:
    # (u, created) = User.objects.get_or_create(username=_address, password="test")
    p = UserProfile.objects.get_or_create(_address)
    # p = UserProfile.objects.create(user=u, initial_context_id=_address)
    return p


@patch(
    "faucet.faucet_manager.bright_id_interface.BrightIDInterface.sponsor",
    lambda a, b: True,
)
def create_verified_user() -> UserProfile:
    user = create_new_user("0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e")
    user._verification_status = ClaimReceipt.VERIFIED
    user._last_verified_datetime = timezone.now()
    user.save()
    return user


def create_new_wallet(user_profile, _address, wallet_type) -> Wallet:
    wallet, is_create = Wallet.objects.get_or_create(
        user_profile=user_profile, address=_address, wallet_type=wallet_type
    )
    return wallet


class CheckUsernameTestCase(APITestCase):
    def setUp(self) -> None:
        self.endpoint = "AUTHENTICATION:check-username"
        self.user_profile = UserProfile.objects.get_or_create("mamad")
        self.user = self.user_profile.user
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()
        self.user_profile.username = "mamad"
        self.user_profile.save()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_username_is_invalid(self):
        response = self.client.post(reverse(self.endpoint), {"username": "mamad%^"})
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse(self.endpoint), {"username": "______"})
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse(self.endpoint), {"username": "mm"})
        self.assertEqual(response.status_code, 403)

    def test_username_is_not_available(self):
        response = self.client.post(reverse(self.endpoint), {"username": "mamad"})
        self.assertEqual(response.status_code, 409)

    def test_username_is_available(self):
        response = self.client.post(reverse(self.endpoint), {"username": "mamad1"})
        self.assertEqual(response.status_code, 200)


class SetUsernameTestCase(APITestCase):
    def setUp(self) -> None:
        self.endpoint = "AUTHENTICATION:set-username"
        self.user_profile = UserProfile.objects.get_or_create("reza")
        self.user = self.user_profile.user
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()
        self.user_profile.username = "reza"
        self.user_profile.save()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_username_is_invalid(self):
        response = self.client.post(reverse(self.endpoint), {"username": "reza%^"})
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse(self.endpoint), {"username": "______"})
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse(self.endpoint), {"username": "rr"})
        self.assertEqual(response.status_code, 400)

    def test_username_is_not_available(self):
        response = self.client.post(reverse(self.endpoint), {"username": "reza"})
        self.assertEqual(response.status_code, 400)

    def test_username_is_available(self):
        response = self.client.post(reverse(self.endpoint), {"username": "reza2"})
        self.assertEqual(response.status_code, 200)


class TestUserLogin(APITestCase):
    def setUp(self) -> None:
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"
        self.endpoint = reverse("AUTHENTICATION:login-user")

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b, c: (True, None),
    )
    def test_not_providing_arguments_should_be_forbidden(self):
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.check_sponsorship",
        lambda a, b: False,
    )
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.sponsor",
        lambda a, b: False,
    )
    def test_check_in_process_of_sponsoring(self):
        response = self.client.post(self.endpoint, data={"username": self._address, "password": self.password})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.check_sponsorship",
        lambda a, b: False,
    )
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.sponsor",
        lambda a, b: True,
    )
    def test_check_requested_brightID_and_waiting_for_that(self):
        response = self.client.post(self.endpoint, data={"username": self._address, "password": self.password})
        self.assertEqual(response.status_code, HTTP_409_CONFLICT)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.check_sponsorship",
        lambda a, b: True,
    )
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.get_verification_status",
        lambda a, b: (False, 4),
    )
    def test_linking_process_should_be_failed(self):
        response = self.client.post(self.endpoint, data={"username": self._address, "password": self.password})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


class TestSponsorCheckOrMakeSponsored(APITestCase):
    def setUp(self) -> None:
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"
        self.endpoint = reverse("AUTHENTICATION:sponsor-user")

    def test_invalid_arguments_provide_should_fail(self):
        response = self.client.post(self.endpoint, data={"somthing_else": False})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.create_verification_link",
        lambda a, b: None,
    )
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.create_qr_content",
        lambda a, b: None,
    )
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.check_sponsorship",
        lambda a, b: True,
    )
    def test_already_sponsored_is_ok(self):
        response = self.client.post(self.endpoint, data={"address": self._address})
        self.assertEqual(response.status_code, HTTP_200_OK)

    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.create_verification_link",
        lambda a, b: None,
    )
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.create_qr_content",
        lambda a, b: None,
    )
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.check_sponsorship",
        lambda a, b: False,
    )
    @patch(
        "authentication.helpers.BrightIDSoulboundAPIInterface.sponsor",
        lambda a, b: True,
    )
    def test_become_sponsor(self):
        response = self.client.post(self.endpoint, data={"address": self._address})
        self.assertEqual(response.status_code, HTTP_200_OK)


class TestListCreateWallet(APITestCase):
    def setUp(self) -> None:
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461G3Ef9A9"
        self.endpoint = reverse("AUTHENTICATION:wallets-user")
        self.user_profile = create_new_user()
        self.client.force_authenticate(user=self.user_profile.user)

    def test_invalid_arguments_provided_should_fail(self):
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post(self.endpoint, data={"address": False})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post(self.endpoint, data={"wallet_type": False})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_wallet_address(self):
        response = self.client.post(self.endpoint, data={"address": self._address, "wallet_type": "EVM"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_create_same_address_twice(self):
        response = self.client.post(self.endpoint, data={"address": self._address, "wallet_type": "EVM"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        response = self.client.post(self.endpoint, data={"address": self._address, "wallet_type": "EVM"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_get_wallet_list(self):
        response = self.client.post(self.endpoint, data={"address": self._address, "wallet_type": "EVM"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        response = self.client.get(self.endpoint, {"wallet_type": "EVM"})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertGreater(len(response.data), 0)


class TestWalletView(APITestCase):
    def setUp(self) -> None:
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"
        self.user_profile = create_new_user()
        create_new_wallet(self.user_profile, self._address, "EVM")
        self.endpoint = reverse("AUTHENTICATION:wallets-user")
        self.client.force_authenticate(user=self.user_profile.user)

    def test_request_to_this_api_is_ok(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, HTTP_200_OK)

    # def test_change_primary_ture(self):
    #     response: Response = self.client.patch(self.endpoint, data={'primary': True})
    #     self.assertEqual(response.status_code, HTTP_200_OK)
    #     self.assertEqual(response.data.get('primary'), True)

    # def test_access_to_another_user_wallet(self):
    #     _address = '0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A2'
    #     other_user = create_new_user(_address)
    #     wallet = create_new_wallet(other_user, _address, 'EVM')
    #     _endpoint = reverse('AUTHENTICATION:wallet-user', kwargs={'pk': wallet.pk})
    #     response = self.client.get(_endpoint)
    #     self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class TestGetProfileView(APITestCase):
    def setUp(self) -> None:
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"
        self.endpoint = reverse("AUTHENTICATION:get-profile-user")
        self.user_profile = create_new_user()
        self.client.force_authenticate(user=self.user_profile.user)

    def test_request_to_this_api_is_ok(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, HTTP_200_OK)
