from django.urls import path


urlpatterns = [
    path("telegram/login/", TelegramLoginView.as_view(), name="telegram-login"),
    path(
        "telegram/login/callback/",
        TelegramLoginCallbackView.as_view(),
        name="telegram-login-callback",
    ),
]
