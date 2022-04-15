from django.urls import path

from faucet.views import CreateUserView, GetVerificationUrlView

app_name = "FAUCET"

urlpatterns = [
    path("user/create/", CreateUserView.as_view(), name="create-user"),
    path("user/<address>/verification-url/", GetVerificationUrlView.as_view(), name="get-verification-url"),
]
