from django.urls import path
from prizetap.views import *

urlpatterns = [
    path(
        "raffle-list/",
        RaffleListView.as_view(),
        name="raffle-list",
    ),
    path(
        "raffle-enrollment/<int:pk>/",
        RaffleEnrollmentView.as_view(),
        name="raflle-enrollment",
    ),
    path(
        "claim-prize/<int:pk>/",
        ClaimPrizeView.as_view(),
        name="claim-prize",
    ),
    path(
        "set-enrollment-tx/<int:pk>/",
        SetEnrollmentTxView.as_view(),
        name="set-enrollment-tx",
    ),
    path(
        "set-claiming-prize-tx/<int:pk>/",
        SetClaimingPrizeTxView.as_view(),
        name="set-claiming-prize-tx",
    )
]
