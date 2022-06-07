from rest_framework.test import APITestCase

from faucet.fund_manager.fund_manager import FundManager

class TestFundManager(APITestCase):
    def setUp(self) -> None:
        # self.account = 
        pass
    
    def test_create_fund_manager(self):
        fund_manager = FundManager()