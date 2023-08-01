from unittest.mock import patch, PropertyMock
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from authentication.models import UserProfile
from .constraints import BrightIDMeetVerification, BrightIDAuraVerification

class BaseTestCase(APITestCase):
    def setUp(self):
        self.user_profile = UserProfile.objects.create(
            user=User.objects.create_user(
                username="test", 
                password="1234"
            ),
            initial_context_id="test",
            username="test",
        )

class ConstraintTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    @patch('authentication.models.UserProfile.is_meet_verified', new_callable=PropertyMock)
    def test_meet_constraint(self, is_meet_verified_mock:PropertyMock):
        is_meet_verified_mock.return_value = False
        constraint = BrightIDMeetVerification(self.user_profile)
        self.assertEqual(constraint.is_observed(), False)
        self.assertEqual(constraint.response(), "BrightIDMeetVerification constraint is violated")

    @patch('authentication.models.UserProfile.is_aura_verified', new_callable=PropertyMock)
    def test_aura_constraint(self, is_aura_verified_mock:PropertyMock):
        is_aura_verified_mock.return_value = False
        constraint = BrightIDAuraVerification(self.user_profile)
        self.assertEqual(constraint.is_observed(), False)
        self.assertEqual(constraint.response(), "BrightIDAuraVerification constraint is violated")