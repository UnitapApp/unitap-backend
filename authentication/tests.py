from django.urls import reverse
from authentication.models import UserProfile
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Create your tests here.

### get address as username and signed address as password and verify signature

### retrieve address from brightID


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
