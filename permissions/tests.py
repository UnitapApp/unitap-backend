from rest_framework.test import APITestCase
from .models import Permission, BrightIDMeetVerification, BrightIDAuraVerification


class PermissionsTestCase(APITestCase):
    def setUp(self) -> None:
        pass

    def test_permissions_creation(self):
        p = BrightIDMeetVerification.objects.create(name="BrightID Meet Verification")
        self.assertEqual(Permission.objects.count(), 1)
        self.assertEqual(Permission.objects.first(), p)

        p2 = BrightIDAuraVerification.objects.create(name="BrightID Aura Verification")
        self.assertEqual(Permission.objects.count(), 2)
        self.assertEqual(Permission.objects.last(), p2)
