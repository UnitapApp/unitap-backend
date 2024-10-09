from django.urls import path
from .views import TelegramLoginCallbackView, TelegramLoginView


urlpatterns = [
    path("login/", TelegramLoginView.as_view(), name="telegram-login"),
    path(
        "login/callback/",
        TelegramLoginCallbackView.as_view(),
        name="telegram-login-callback",
    ),
]
