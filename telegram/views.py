from rest_framework.views import APIView
from rest_framework.response import Response
from django_telegram_login.widgets.generator import create_redirect_login_widget
from django_telegram_login.authentication import verify_telegram_authentication
from django.conf import settings

from core.thirdpartyapp.telegram import TelegramUtil


class TelegramLoginView(APIView):
    def get(self, request):
        telegram_login_widget = TelegramUtil().create_telegram_widget(
            "/api/telegram/login/callback"
        )
        return Response({"login_url": telegram_login_widget})


class TelegramLoginCallbackView(APIView):
    def post(self, request):
        telegram_data = request.data
        is_verified = TelegramUtil().verify_login(telegram_data)

        if is_verified:
            user_id = telegram_data["id"]
            username = telegram_data["username"]

            return Response(
                {"status": "success", "user_id": user_id, "username": username}
            )
        else:
            return Response({"status": "error"}, status=400)
