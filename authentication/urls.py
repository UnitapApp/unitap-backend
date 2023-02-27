from django.urls import path
from authentication.views import LoginView


app_name = "AUTHENTICATION"

urlpatterns = [path("user/login/", LoginView.as_view(), name="login-user")]
