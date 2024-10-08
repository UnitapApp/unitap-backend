from django.urls import path
from django.views.decorators.cache import cache_page

from prizetap.views import (
    ConstraintsListView,
    CreateRaffleView,
    GetRaffleConstraintsView,
    GetRaffleEntryView,
    LineaRaffleView,
    RaffleDetailsView,
    RaffleEnrollmentView,
    RaffleEntriesView,
    RaffleListView,
    SetClaimingPrizeTxView,
    SetEnrollmentTxView,
    SetLineaTxHashView,
    SetRaffleTXView,
    UserRafflesListView,
    ValidChainsView,
)

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
    ),
    path(
        "get-raffle-constraints/<int:raffle_pk>/",
        GetRaffleConstraintsView.as_view(),
        name="get-raffle-constraints",
    ),
    path(
        "create-raffle/",
        CreateRaffleView.as_view(),
        name="create-raffle",
    ),
    path(
        "get-valid-chains/",
        cache_page(60 * 2)(ValidChainsView.as_view()),
        name="get-valid-chains",
    ),
    path(
        "get-user-raffles/",
        UserRafflesListView.as_view(),
        name="get-user-raffles",
    ),
    path(
        "get-constraints/",
        cache_page(60 * 2)(ConstraintsListView.as_view()),
        name="get-constraints",
    ),
    path(
        "set-raffle-tx/<int:pk>/",
        SetRaffleTXView.as_view(),
        name="set-raffle-tx",
    ),
    path(
        "get-linea-entries/",
        cache_page(60 * 15)(LineaRaffleView.as_view()),
        name="get-linea-entries",
    ),
    path(
        "set-linea-hash/<int:pk>/",
        SetLineaTxHashView.as_view(),
        name="set-linea-hash",
    ),
    path(
        "raffle-details/<int:pk>/", RaffleDetailsView.as_view(), name="raffle-details"
    ),
    path(
        "raffle-entries/<int:pk>/", RaffleEntriesView.as_view(), name="raffle-entries"
    ),
]
