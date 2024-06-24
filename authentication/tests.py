import datetime
import json
from unittest.mock import patch

from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from eth_account import Account
from eth_account.messages import encode_typed_data
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)
from rest_framework.test import APITestCase

from authentication.models import (
    DiscordConnection,
    ENSConnection,
    GitcoinPassportConnection,
    UserProfile,
    Wallet,
)
from core.thirdpartyapp.discord import DiscordUtils
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
    _address="0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef888",
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
        response = self.client.post(
            self.endpoint, data={"username": self._address, "password": self.password}
        )
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
        response = self.client.post(
            self.endpoint, data={"username": self._address, "password": self.password}
        )
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
        response = self.client.post(
            self.endpoint, data={"username": self._address, "password": self.password}
        )
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
        self._address2 = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461G3Ef9A91"
        self.private_key_test1 = (
            "2534fa7456f3aaf0f72ece66434a7d380d08cee47d8a2db56c08a3048890b50f"
        )
        self.public_key_test1 = "0xD8Be96705B9fb518eEb2758719831BAF6C6E5E05"
        self.endpoint = reverse("AUTHENTICATION:wallets-user")
        self.user_profile = create_new_user()
        self.client.force_authenticate(user=self.user_profile.user)

    def create_and_sign_message(self):
        timestamp = datetime.datetime.now().isoformat() + "Z"

        message = {
            "message": {
                "message": "Unitap Sign In",
                "URI": "https://unitap.app",
                "IssuedAt": str(timestamp),
            },
            "primaryType": "Unitap",
            "account": "0xFd7716d8B0786349C6515C3aDBadD12a093E6573",
            "domain": {
                "name": "Unitap Connect",
                "version": "1",
                "chainId": 10,
                "verifyingContract": "0x0000000000000000000000000000000000000000",
            },
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Unitap": [
                    {"name": "message", "type": "string"},
                    {"name": "URI", "type": "string"},
                    {"name": "IssuedAt", "type": "string"},
                ],
            },
        }

        hashed_message = encode_typed_data(full_message=message)

        account = Account.from_key(self.private_key_test1)
        signed_message = account.sign_message(hashed_message)
        signature = signed_message.signature.hex()

        return message, signature

    def test_invalid_arguments_provided_should_fail(self):
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post(self.endpoint, data={"address": False})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post(self.endpoint, data={"wallet_type": False})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_wallet_address(self):
        message, signature = self.create_and_sign_message()

        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_create_same_address_twice(self):
        message, signature = self.create_and_sign_message()

        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_same_address_for_another_user(self):
        message, signature = self.create_and_sign_message()

        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        user_profile_2 = create_new_user(self._address2)
        self.client.force_authenticate(user=user_profile_2.user)
        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_same_address_after_delete(self):
        message, signature = self.create_and_sign_message()

        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        create_new_wallet(self.user_profile, self._address2, "EVM")

        endpoint = reverse(
            "AUTHENTICATION:wallet-user", kwargs={"pk": response.data.get("pk")}
        )
        response = self.client.delete(endpoint)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_create_same_address_after_delete_for_another_user(self):
        message, signature = self.create_and_sign_message()

        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        create_new_wallet(self.user_profile, self._address2, "EVM")

        endpoint = reverse(
            "AUTHENTICATION:wallet-user", kwargs={"pk": response.data.get("pk")}
        )
        response = self.client.delete(endpoint)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

        user_profile_2 = create_new_user(self._address2)
        self.client.force_authenticate(user=user_profile_2.user)

        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_get_wallet_list(self):
        message, signature = self.create_and_sign_message()

        response = self.client.post(
            self.endpoint,
            data={
                "address": self.public_key_test1,
                "wallet_type": "EVM",
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        response = self.client.get(self.endpoint, {"wallet_type": "EVM"})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertGreater(len(response.data), 0)


class TestWalletView(APITestCase):
    def setUp(self) -> None:
        self.password = "test"
        self._address = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9"
        self._address2 = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A1"
        self._address3 = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A3"
        self.user_profile = create_new_user()
        self.wallet = create_new_wallet(self.user_profile, self._address, "EVM")
        self.endpoint = reverse(
            "AUTHENTICATION:wallet-user", kwargs={"pk": self.wallet.pk}
        )
        self.client.force_authenticate(user=self.user_profile.user)

    def test_request_to_this_api_is_ok(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_user_wallet_when_has_one_wallet(self):
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_user_wallet_when_has_two_wallet(self):
        _ = create_new_wallet(
            user_profile=self.user_profile, _address=self._address2, wallet_type="EVM"
        )
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_create_after_delete_wallet(self):
        _ = create_new_wallet(
            user_profile=self.user_profile, _address=self._address2, wallet_type="EVM"
        )
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertRaises(
            IntegrityError, create_new_wallet, self.user_profile, self._address, "EVM"
        )

    def test_assign_deleted_wallet_to_another_user(self):
        user_2 = create_new_user(self._address2)
        _ = create_new_wallet(
            user_profile=self.user_profile, _address=self._address2, wallet_type="EVM"
        )
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertRaises(
            IntegrityError, create_new_wallet, user_2, self._address, "EVM"
        )


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


class TestCheckUserExistsView(APITestCase):
    def setUp(self) -> None:
        self.user_profile = create_new_user()
        Wallet.objects.create(
            user_profile=self.user_profile, wallet_type="EVM", address=address
        )

    def test_check_user_exists(self):
        response = self.client.post(
            reverse("AUTHENTICATION:check-user-exists"),
            data={"wallet_address": address},
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["exists"], True)

    def test_check_user_not_exists(self):
        response = self.client.post(
            reverse("AUTHENTICATION:check-user-exists"),
            data={"wallet_address": "0x90F8bf6A479f320ead074411a4B0e44Ea8c9C2"},
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["exists"], False)


class TestVerifyLoginSignature(APITestCase):
    def setUp(self) -> None:
        self.endpoint = reverse("AUTHENTICATION:wallet-login")
        self.private_key_test1 = (
            "2534fa7456f3aaf0f72ece66434a7d380d08cee47d8a2db56c08a3048890b50f"
        )
        self.public_key_test1 = "0xD8Be96705B9fb518eEb2758719831BAF6C6E5E05"

    def create_and_sign_message(self):
        timestamp = datetime.datetime.now().isoformat() + "Z"

        message = {
            "message": {
                "message": "Unitap Sign In",
                "URI": "https://unitap.app",
                "IssuedAt": str(timestamp),
            },
            "primaryType": "Unitap",
            "account": "0xFd7716d8B0786349C6515C3aDBadD12a093E6573",
            "domain": {
                "name": "Unitap Connect",
                "version": "1",
                "chainId": 10,
                "verifyingContract": "0x0000000000000000000000000000000000000000",
            },
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Unitap": [
                    {"name": "message", "type": "string"},
                    {"name": "URI", "type": "string"},
                    {"name": "IssuedAt", "type": "string"},
                ],
            },
        }

        hashed_message = encode_typed_data(full_message=message)

        account = Account.from_key(self.private_key_test1)
        signed_message = account.sign_message(hashed_message)
        signature = signed_message.signature.hex()

        return message, signature

    def test_api_verify_login_signature(self):
        message, signature = self.create_and_sign_message()

        result = self.client.post(
            self.endpoint,
            data={
                "wallet_address": self.public_key_test1,
                "message": json.dumps(message),
                "signature": signature,
            },
        )

        self.assertEqual(result.status_code, HTTP_200_OK)

    def test_api_verify_login_signature_with_deleted_wallet(self):
        message, signature = self.create_and_sign_message()

        result = self.client.post(
            self.endpoint,
            data={
                "wallet_address": self.public_key_test1,
                "message": json.dumps(message),
                "signature": signature,
            },
        )
        self.assertEqual(result.status_code, HTTP_200_OK)

        wallet = Wallet.objects.get(address=self.public_key_test1)
        wallet.delete()

        result = self.client.post(
            self.endpoint,
            data={
                "wallet_address": self.public_key_test1,
                "message": json.dumps(message),
                "signature": signature,
            },
        )

        self.assertEqual(result.status_code, HTTP_400_BAD_REQUEST)


class TestGitcoinPassportThirdPartyConnection(APITestCase):
    def setUp(self) -> None:
        self.address = "0x0cE49AF5d8c5A70Edacd7115084B2b3041fE4fF6"
        self.user_profile = create_new_user()
        create_new_wallet(
            user_profile=self.user_profile, _address=self.address, wallet_type="EVM"
        )

    def test_gitcoin_passport_connection_successful(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("AUTHENTICATION:connect-gitcoin-passport"),
            data={"user_wallet_address": self.address},
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(
            GitcoinPassportConnection.objects.filter(
                user_profile=self.user_profile, user_wallet_address=self.address
            ).count(),
            1,
        )

    def test_gitcoin_passport_not_exists(self):
        address_does_not_have_gitcoin_passport = (
            "0x0cE49AF5d8c5A70Edacd7115084B2b3041fE4fF5"
        )
        create_new_wallet(
            user_profile=self.user_profile,
            _address=address_does_not_have_gitcoin_passport,
            wallet_type="EVM",
        )
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("AUTHENTICATION:connect-gitcoin-passport"),
            data={"user_wallet_address": address_does_not_have_gitcoin_passport},
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_address_not_owned_by_user(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("AUTHENTICATION:connect-gitcoin-passport"),
            data={"user_wallet_address": address},
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)


class TestENSThirdPartyConnection(APITestCase):
    def setUp(self) -> None:
        self.address = "0x0cE49AF5d8c5A70Edacd7115084B2b3041fE4fF6"
        self.user_profile = create_new_user()
        create_new_wallet(
            user_profile=self.user_profile, _address=self.address, wallet_type="EVM"
        )

    @patch(
        "authentication.thirdpartydrivers.ens.ENSDriver.get_name",
        lambda a, b: "test",
    )
    def test_ens_connection_successful(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("AUTHENTICATION:connect-ens"),
            data={"user_wallet_address": self.address},
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(
            ENSConnection.objects.filter(
                user_profile=self.user_profile, user_wallet_address=self.address
            ).count(),
            1,
        )

    @patch(
        "authentication.thirdpartydrivers.ens.ENSDriver.get_name",
        lambda a, b: "test",
    )
    def test_address_not_owned_by_user(self):
        self.client.force_authenticate(user=self.user_profile.user)
        response = self.client.post(
            reverse("AUTHENTICATION:connect-ens"),
            data={"user_wallet_address": address},
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    @patch(
        "authentication.thirdpartydrivers.ens.ENSDriver.get_name",
        lambda a, b: "test",
    )
    def test_ens_disconnect_successful(self):
        self.client.force_authenticate(user=self.user_profile.user)
        self.client.post(
            reverse("AUTHENTICATION:connect-ens"),
            data={"user_wallet_address": self.address},
        )
        ens_instance = ENSConnection.objects.get(
            user_profile=self.user_profile, user_wallet_address=self.address
        )
        response = self.client.delete(
            reverse("AUTHENTICATION:disconnect-ens", kwargs={"pk": ens_instance.pk}),
        )
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(
            ENSConnection.objects.filter(
                user_profile=self.user_profile, user_wallet_address=self.address
            ).count(),
            0,
        )


class TestDiscordConnection(APITestCase):
    def setUp(self):
        self.user = create_new_user()

    def test_discord_connection_creation(self):
        connection = DiscordConnection.objects.create(
            user_profile=self.user,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
        )
        self.assertEqual(DiscordConnection.objects.count(), 1)
        self.assertEqual(connection.user_profile, self.user)
        self.assertEqual(connection.access_token, "test_access_token")
        self.assertEqual(connection.refresh_token, "test_refresh_token")

    def test_discord_connection_update(self):
        connection = DiscordConnection.objects.create(
            user_profile=self.user,
            access_token="old_access_token",
            refresh_token="old_refresh_token",
        )
        connection.access_token = "new_access_token"
        connection.refresh_token = "new_refresh_token"
        connection.save()

        updated_connection = DiscordConnection.objects.get(user_profile=self.user)
        self.assertEqual(updated_connection.access_token, "new_access_token")
        self.assertEqual(updated_connection.refresh_token, "new_refresh_token")


class TestDiscordUtils(APITestCase):
    @patch("core.thirdpartyapp.discord.DiscordUtils.get_authorization_url")
    def test_get_authorization_url(self, mock_get_auth_url):
        mock_get_auth_url.return_value = "https://discord.com/api/oauth2/\
            authorize?client_id=123&redirect_uri=http://localhost:8000/callback\
                &response_type=code&scope=identify%20guilds"
        url = DiscordUtils.get_authorization_url()
        self.assertTrue(url.startswith("https://discord.com/api/oauth2/authorize"))
        self.assertIn("client_id", url)
        self.assertIn("redirect_uri", url)
        self.assertIn("response_type=code", url)
        self.assertIn("scope=identify%20guilds", url)

    @patch("core.thirdpartyapp.discord.DiscordUtils.get_tokens")
    def test_get_tokens(self, mock_get_tokens):
        mock_get_tokens.return_value = ("access_token", "refresh_token")
        access_token, refresh_token = DiscordUtils.get_tokens("test_code")
        self.assertEqual(access_token, "access_token")
        self.assertEqual(refresh_token, "refresh_token")

    @patch("core.thirdpartyapp.discord.DiscordUtils.get_user_info")
    def test_get_user_info(self, mock_get_user_info):
        mock_user_info = {
            "id": "12345",
            "username": "testuser",
            "discriminator": "1234",
            "avatar": "avatar_hash",
        }
        mock_get_user_info.return_value = mock_user_info
        user_info = DiscordUtils.get_user_info("test_access_token")
        self.assertEqual(user_info, mock_user_info)

    @patch("core.thirdpartyapp.discord.DiscordUtils.get_user_guilds")
    def test_get_user_guilds(self, mock_get_user_guilds):
        mock_guilds = [{"id": "1", "name": "Guild 1"}, {"id": "2", "name": "Guild 2"}]
        mock_get_user_guilds.return_value = mock_guilds
        guilds = DiscordUtils.get_user_guilds("test_access_token")
        self.assertEqual(guilds, mock_guilds)
