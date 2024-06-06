from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import BrightIDConnection, GitcoinPassportConnection, UserProfile
from unittest.mock import patch

class GetUserAnalyticsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/analytics/'  
    

    
    @patch('authentication.models.UserProfile.user_count')
    @patch('authentication.models.BrightIDConnection.objects.all')
    @patch('authentication.models.GitcoinPassportConnection.objects.all')
    def test_get_user_analytics_cache_not_empty(self, mock_gitcoinpassport_all, mock_brightid_all, mock_user_count):
        mock_user_count.return_value = 100
        mock_brightid_all.return_value.count.return_value = 50
        mock_gitcoinpassport_all.return_value.count.return_value = 30
        
        cache.set("analytics_users_count", {
            "allUsersCount": 50,
            "brightidUsersCount": 20,
            "gitcoinpassportUsersCount": 10,
        })
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_data = {
            "allUsersCount": 50,
            "brightidUsersCount": 20,
            "gitcoinpassportUsersCount": 10,
        }
        self.assertEqual(response.data["allUsersCount"], expected_data["allUsersCount"])
        self.assertEqual(response.data["brightidUsersCount"], expected_data["brightidUsersCount"])
        self.assertEqual(response.data["gitcoinpassportUsersCount"], expected_data["gitcoinpassportUsersCount"])
        
        cached_data = cache.get("analytics_users_count")

        self.assertEqual(cached_data["allUsersCount"], expected_data["allUsersCount"])
        self.assertEqual(cached_data["brightidUsersCount"], expected_data["brightidUsersCount"])
        self.assertEqual(cached_data["gitcoinpassportUsersCount"], expected_data["gitcoinpassportUsersCount"])
