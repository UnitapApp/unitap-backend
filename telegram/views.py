from rest_framework.views import CreateApiView
from rest_framework.response import Response

from telegram.models import TelegramConnection
from core.thirdpartyapp.telegram import TelegramUtil

from .bot import tbot

from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt


import telebot
import requests


def get_telegram_safe_ips():
    telegram_ips_cache = cache.get("telegram_safe_ip_list")

    if telegram_ips_cache:
        return telegram_ips_cache

    telegram_ips = requests.get("https://core.telegram.org/bots/webhooks").json()[
        "ip_ranges"
    ]

    cache.set("telegram_safe_ip_list", telegram_ips, 800)

    return telegram_ips


@csrf_exempt
def telebot_respond(request):
    client_ip = request.META["REMOTE_ADDR"]

    telegram_ips = get_telegram_safe_ips

    # Validate the request's IP address against Telegram's IP ranges
    if client_ip not in telegram_ips:
        raise PermissionDenied("Invalid IP address")

    if (
        request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        != settings.TELEGRAM_BOT_API_SECRET
    ):
        raise PermissionDenied("Invalid secret token")

    if request.META["CONTENT_TYPE"] == "application/json":
        json_data = request.body.decode("utf-8")
        update = telebot.types.Update.de_json(json_data)
        tbot.process_new_updates([update])
        return HttpResponse("")

    else:
        raise PermissionDenied


class TelegramLoginCallbackView(CreateApiView):

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
