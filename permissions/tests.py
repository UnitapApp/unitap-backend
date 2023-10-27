# from rest_framework.test import APITestCase
# from .models import *


# class PermissionsTestCase(APITestCase):
#     def setUp(self) -> None:
#         pass

#     def test_permissions_creation(self):
#         p = BrightIDMeetVerification.objects.create(name="BrightID Meet Verification")
#         self.assertEqual(Permission.objects.count(), 1)
#         self.assertEqual(Permission.objects.first(), p)

#         p2 = BrightIDAuraVerification.objects.create(name="BrightID Aura Verification")
#         self.assertEqual(Permission.objects.count(), 2)
#         self.assertEqual(Permission.objects.last(), p2)

#         p3 = OncePerWeekVerification.objects.create(name="Once Per Week Verification")
#         self.assertEqual(Permission.objects.count(), 3)
#         self.assertEqual(Permission.objects.last(), p3)

#         p4 = OncePerMonthVerification.objects.create(name="Once Per Month Verification")
#         self.assertEqual(Permission.objects.count(), 4)
#         self.assertEqual(Permission.objects.last(), p4)

#         p5 = OnceInALifeTimeVerification.objects.create(name="Once In A Life Time Verification")
#         self.assertEqual(Permission.objects.count(), 5)
#         self.assertEqual(Permission.objects.last(), p5)
