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
        "raffle-enrollment/detail/<int:pk>/",
        GetRaffleEntryView.as_view(),
        name="raflle-enrollment-detail",
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
