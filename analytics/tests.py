import unittest
from unittest.mock import patch
from analytics.models import UserProfile, BrightIDConnection, GitcoinPassportConnection, UserAnalytics

class TestUpdateData(unittest.TestCase):
    @patch.object(UserProfile, 'user_count')
    @patch.object(BrightIDConnection.objects, 'all')
    @patch.object(GitcoinPassportConnection.objects, 'all')
    @patch.object(UserAnalytics.objects, 'create')
    def test_updateData(self, mock_create, mock_gitcoin_all, mock_brightid_all, mock_user_count):
        # Arrange
        mock_user_count.return_value = 10
        mock_brightid_all.return_value.count.return_value = 5
        mock_gitcoin_all.return_value.count.return_value = 3
    
        # Act
        UserAnalytics.updateData()

        # Assert
        mock_create.assert_called_once_with(all_users_count=10, brightid_users_count=5, gitcoinpassport_users_count=3)

if __name__ == '__main__':
    unittest.main()