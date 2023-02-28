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
        "user/set-lightning-wallet/",
        SetBitcoinLightningWalletAddressView.as_view(),
        name="set-lightning-wallet-user",
    ),
    path(
        "user/get-lightning-wallet/",
        GetBitcoinLightningWalletAddressView.as_view(),
        name="get-lightning-wallet-user",
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
    path(
        "user/delete-solana-wallet/",
        DeleteSolanaWalletAddressView.as_view(),
        name="delete-solana-wallet-user",
    ),
    path(
        "user/delete-lightning-wallet/",
        DeleteBitcoinLightningWalletAddressView.as_view(),
        name="delete-lightning-wallet-user",
    ),
    path(
        "user/delete-evm-wallet/",
        DeleteEVMWalletAddressView.as_view(),
        name="delete-evm-wallet-user",
    ),
    path(
        "user/get-wallets/",
        GetWalletsView.as_view(),
        name="get-wallets-user",
    ),
]
