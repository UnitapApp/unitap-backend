from django.urls import path

from faucet.views import (
    ChainListView,
    ClaimMaxView,
    GlobalSettingsView,
    LastClaimView,
    ListClaims,
    GetTotalWeeklyClaimsRemainingView,
    artwork_video,
    error500,
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
        GetTotalWeeklyClaimsRemainingView.as_view(),
        name="remaining-claims",
    ),
    path("user/last-claim/", LastClaimView.as_view(), name="last-claim"),
    path("user/claims/", ListClaims.as_view(), name="claims"),
    path(
        "chain/list/", ChainListView.as_view(), name="chain-list"
    ),  # can have auth token for more user specific info
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
]
