from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import BrightIDConnection, GitcoinPassportConnection, UserProfile
from unittest.mock import patch
from django.urls import reverse

class GetUserAnalyticsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear() 

    def tearDown(self) -> None:
        cache.clear()
    
    @patch('authentication.models.UserProfile.user_count')
    @patch('authentication.models.BrightIDConnection.objects.all')
    @patch('authentication.models.GitcoinPassportConnection.objects.all')
    def test_get_user_analytics_cache_not_empty(self, mock_gitcoinpassport_all, mock_brightid_all, mock_user_count):
        mock_user_count.return_value = 100
        mock_brightid_all.return_value.count.return_value = 50
        mock_gitcoinpassport_all.return_value.count.return_value = 30
        expected_data = {
            "all_users_count": 100,
            "brightid_users_count": 50,
            "gitcoinpassport_users_count": 30,
        }
       
        endpoint = reverse("ANALYTICS:get-user-analytics")

        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
       
        self.assertEqual(response.data["all_users_count"], expected_data["all_users_count"])
        self.assertEqual(response.data["brightid_users_count"], expected_data["brightid_users_count"])
        self.assertEqual(response.data["gitcoinpassport_users_count"], expected_data["gitcoinpassport_users_count"])
        
        # second request
        response2 = self.client.get(endpoint)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
       
        self.assertEqual(response2.data["all_users_count"], expected_data["all_users_count"])
        self.assertEqual(response2.data["brightid_users_count"], expected_data["brightid_users_count"])
        self.assertEqual(response2.data["gitcoinpassport_users_count"], expected_data["gitcoinpassport_users_count"])