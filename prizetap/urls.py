from django.urls import path
from prizetap.views import *

urlpatterns = [
    path(
        "raffle-list/",
        RaffleListView.as_view(),
        name="raffle-list",
    ),
]
