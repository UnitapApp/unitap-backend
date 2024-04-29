from django.urls import path
from django.views.decorators.cache import cache_page

from authentication.views import (
    CheckUserExistsView,
    CheckUsernameView,
    ConnectBrightIDView,
    GetProfileView,
    GitcoinPassportConnectionView,
    LoginRegisterView,
    LoginView,
    SetUsernameView,
    SponsorView,
    TwitterOAuthCallbackView,
    TwitterOAuthView,
    UserHistoryCountView,
    UserProfileCountView,
    UserThirdPartyConnectionsView,
    WalletListCreateView,
    WalletView,
)

app_name = "AUTHENTICATION"

urlpatterns = [
    path("user/login/", LoginView.as_view(), name="login-user"),
    path("user/wallet-login/", LoginRegisterView.as_view(), name="wallet-login"),
    path(
        "user/count/",
        cache_page(60 * 15)(UserProfileCountView.as_view()),
        name="user-count",
    ),
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
    path(
        "user/check-exists/",
        CheckUserExistsView.as_view(),
        name="check-user-exists",
    ),
    path("user/info/", GetProfileView.as_view(), name="get-profile-user"),
    path("user/sponsor/", SponsorView.as_view(), name="sponsor-user"),
    path(
        "user/connect/brightid/", ConnectBrightIDView.as_view(), name="connect-brightid"
    ),
    path(
        "user/all-connections/",
        UserThirdPartyConnectionsView.as_view(),
        name="all-connections",
    ),
    path(
        "user/history-count/",
        cache_page(60 * 1)(UserHistoryCountView.as_view()),
        name="user-history-count",
    ),
    path(
        "user/connect/gitcoin-passport/",
        GitcoinPassportConnectionView.as_view(),
        name="connect-gitcoin-passport",
    ),
    path("twitter/", TwitterOAuthView.as_view(), name="twitter-oauth"),
    path(
        "twitter/callback/",
        TwitterOAuthCallbackView.as_view(),
        name="twitter-oauth-callback",
    ),
]
