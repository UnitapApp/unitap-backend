from django.urls import path
from .views import TelegramLoginCallbackView, telebot_respond


urlpatterns = [
    path(
        "login/callback/",
        TelegramLoginCallbackView.as_view(),
        name="telegram-login-callback",
    ),
    path("wh/", telebot_respond, name="telegram-update-messages"),
]
