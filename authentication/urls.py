from django.urls import path
from authentication.views import *

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
        "user/wallets/",
        WalletListCreateView.as_view(),
        name="wallets-user",
    ),
    path(
        "user/wallets/<int:pk>/",
        WalletView.as_view(),
        name="wallet-user",
    ),
    path("user/info/", GetProfileView.as_view(), name="get-profile-user"),
    path("user/sponsor/", SponsorView.as_view(), name="sponsor-user"),
]
