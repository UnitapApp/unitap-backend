from django.urls import path

from faucet.views import CreateUserView

app_name = "FAUCET"

urlpatterns = [
    path("user/create/", CreateUserView.as_view(), name="create-user"),
]