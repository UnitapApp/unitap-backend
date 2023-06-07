from unittest.mock import patch
from django.urls import reverse
from authentication.models import NetworkTypes, UserProfile, Wallet
from faucet.faucet_manager.credit_strategy import WeeklyCreditStrategy
from faucet.models import Chain, GlobalSettings, WalletAccount
from django.contrib.auth.models import User
from permissions.models import (
    BrightIDAuraVerification,
    BrightIDMeetVerification,
    OncePerWeekVerification,
    OncePerMonthVerification,
)
from rest_framework.test import APITestCase
import inspect
from tokenTap.helpers import (
    create_uint32_random_nonce,
    hash_message,
    sign_hashed_message,
)
from django.utils import timezone
from tokenTap.models import TokenDistribution, TokenDistributionClaim


test_wallet_key = "f57fecd11c6034fd2665d622e866f05f9b07f35f253ebd5563e3d7e76ae66809"
test_rpc_url_private = "http://ganache:7545"
fund_manager = "0x5802f1035AbB8B191bc12Ce4668E3815e8B7Efa0"
x_dai_max_claim = 800e6
gnosis_tokentap_contract_address = "0xB67ec856346b22e4BDA2ab2B53d70D61a2014358"


# Create your tests here.
