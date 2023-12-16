from django.urls import path

from authentication.views import (
    CheckUserExistsView,
    CheckUsernameView,
    DeleteWalletAddressView,
    GetProfileView,
    GetWalletAddressView,
    GetWalletsView,
    LoginView,
    SetUsernameView,
    SetWalletAddressView,
    SponsorView,
    UserProfileCountView,
)

app_name = "AUTHENTICATION"

urlpatterns = [
    path("user/login/", LoginView.as_view(), name="login-user"),
    path("user/count/", UserProfileCountView.as_view(), name="user-count"),
    path(
        "user/set-username/",
        SetUsernameView.as_view(),
        name="set-username",
    ),
    path(
        "user/check-username/",
        CheckUsernameView.as_view(),
        name="check-username",
    ),
    path(
        "user/set-wallet/",
        SetWalletAddressView.as_view(),
        name="set-wallet-user",
    ),
    path(
        "user/get-wallet/",
        GetWalletAddressView.as_view(),
        name="get-wallet-user",
    ),
    path(
        "user/delete-wallet/",
        DeleteWalletAddressView.as_view(),
        name="delete-wallet-user",
    ),
    path(
        "user/get-wallets/",
        GetWalletsView.as_view(),
        name="get-wallets-user",
    ),
    path(
        "user/check-exists/",
        CheckUserExistsView.as_view(),
        name="check-user-exists",
    ),
    path("user/info/", GetProfileView.as_view(), name="get-profile-user"),
    path("user/sponsor/", SponsorView.as_view(), name="sponsor-user"),
]
