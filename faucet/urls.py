from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from faucet.views import (
    ChainBalanceView,
    ChainListView,
    ClaimCountView,
    ClaimMaxView,
    DonationReceiptView,
    GetTotalRoundClaimsRemainingView,
    GlobalSettingsView,
    LastClaimView,
    LeaderboardView,
    ListClaims,
    ListOneTimeClaims,
    SmallChainListView,
    UserLeaderboardView,
    artwork_video,
    error500,
)

schema_view = get_schema_view(
    openapi.Info(
        title="BrightID Gas Faucet API",
        default_version="v0.0.1",
        description="BrightID public gas faucet api docs",
        contact=openapi.Contact(email="snparvizi75@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
)

app_name = "FAUCET"

urlpatterns = [
    path(
        "user/remainig-claims/",
        GetTotalRoundClaimsRemainingView.as_view(),
        name="remaining-claims",
    ),
    path("user/last-claim/", LastClaimView.as_view(), name="last-claim"),
    path("user/claims/", ListClaims.as_view(), name="claims"),
    path("user/one-time-claims/", ListOneTimeClaims.as_view(), name="one-time-claims"),
    path("claims/count/", ClaimCountView.as_view(), name="claims-count"),
    path("chain/list/", ChainListView.as_view(), name="chain-list"),
    path("chain/small-list/", SmallChainListView.as_view(), name="small-chain-list"),
    path(
        "chain/<int:chain_pk>/claim-max/",
        ClaimMaxView.as_view(),
        name="claim-max",
    ),
    path("settings/", GlobalSettingsView.as_view()),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("artwork/video/", artwork_video, name="artwork-video"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("error500", error500),
    path(
        "chain/<int:chain_pk>/balance/",
        ChainBalanceView.as_view(),
        name="chain-balance",
    ),
    path("user/donation/", DonationReceiptView.as_view(), name="donation-receipt"),
    path("gas-tap/leaderboard/", LeaderboardView.as_view(), name="gas-tap-leaderboard"),
    path("user/gas-tap/leaderboard/", UserLeaderboardView.as_view(), name="user-gas-tap-leaderboard"),
]
