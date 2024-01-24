from django.urls import path

from tokenTap.views import (
    ConstraintsListView,
    CreateTokenDistribution,
    GetTokenDistributionConstraintsView,
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
        TokenDistributionListView.as_view(),
        name="token-distribution-list",
    ),
    path(
        "token-distribution/<int:pk>/claim/",
        TokenDistributionClaimView.as_view(),
        name="token-distribution-claim",
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
        ConstraintsListView.as_view(),
        name="get-constraints",
    ),
    path(
        "get-valid-chains/",
        ValidChainsView.as_view(),
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
]
