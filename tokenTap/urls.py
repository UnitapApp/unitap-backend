from django.urls import path
from tokenTap.views import *

urlpatterns = [
    path(
        "token-distribution-list/",
        TokenDistributionListView.as_view(),
        name="token-distribution-list",
    ),
]
