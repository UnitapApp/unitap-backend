from django.urls import path
from tokenTap.views import *

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
]
