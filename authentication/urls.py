from django.urls import path
from authentication.views import *

app_name = "AUTHENTICATION"

urlpatterns = [
    path("user/login/", LoginView.as_view(), name="login-user"),
    path(
        "user/set-evm-wallet/",
        SetEVMWalletAddressView.as_view(),
        name="set-evm-wallet-user",
    ),
    path(
        "user/set-solana-wallet/",
        SetSolanaWalletAddressView.as_view(),
        name="set-solana-wallet-user",
    ),
    path(
        "user/set-bl-wallet/",
        SetBitcoinLightningWalletAddressView.as_view(),
        name="set-bl-wallet-user",
    ),
    path(
        "user/get-bl-wallet/",
        GetBitcoinLightningWalletAddressView.as_view(),
        name="get-bl-wallet-user",
    ),
    path(
        "user/get-evm-wallet/",
        GetEVMWalletAddressView.as_view(),
        name="get-evm-wallet-user",
    ),
    path(
        "user/get-solana-wallet/",
        GetSolanaWalletAddressView.as_view(),
        name="get-solana-wallet-user",
    ),
]
