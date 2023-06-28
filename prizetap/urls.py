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
    )
]
