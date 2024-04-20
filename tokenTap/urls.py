from django.urls import path
from django.views.decorators.cache import cache_page

from tokenTap.views import (
    ClaimDetailView,
    ConstraintsListView,
    CreateTokenDistribution,
    GetTokenDistributionConstraintsView,
    SetDistributionTXView,
    TokenDistributionClaimListView,
    TokenDistributionClaimRetrieveView,
    TokenDistributionClaimStatusUpdateView,
    TokenDistributionClaimView,
    TokenDistributionListView,
    UserTokenDistributionsView,
    ValidChainsView,
)

urlpatterns = [
    path(
        "token-distribution-list/",
        cache_page(60 * 3)(TokenDistributionListView.as_view()),
        name="token-distribution-list",
    ),
    path(
        "token-distribution/<int:pk>/claim/",
        TokenDistributionClaimView.as_view(),
        name="token-distribution-claim",
    ),
    path(
        "claim-detail/<int:pk>/",
        ClaimDetailView.as_view(),
        name="claim-detail",
    ),
    path("claims-list/", TokenDistributionClaimListView.as_view(), name="claims-list"),
    path(
        "claims-list/<int:pk>/",
        TokenDistributionClaimRetrieveView.as_view(),
        name="claim-retrieve",
    ),
    path(
        "claims-list/<int:pk>/update/",
        TokenDistributionClaimStatusUpdateView.as_view(),
        name="claim-update",
    ),
    path(
        "get-token-constraints/<int:td_id>/",
        GetTokenDistributionConstraintsView.as_view(),
        name="get-token-distribution-constraints",
    ),
    path(
        "get-constraints/",
        cache_page(60 * 2)(ConstraintsListView.as_view()),
        name="get-constraints",
    ),
    path(
        "get-valid-chains/",
        cache_page(60 * 3)(ValidChainsView.as_view()),
        name="get-valid-chains",
    ),
    path(
        "create-token-distribution/",
        CreateTokenDistribution.as_view(),
        name="create-token-distribution",
    ),
    path(
        "user-token-distributions/",
        UserTokenDistributionsView.as_view(),
        name="user-token-distributions",
    ),
    path(
        "set-distribution-tx/<int:pk>/",
        SetDistributionTXView.as_view(),
        name="set-distribution-tx",
    ),
]
