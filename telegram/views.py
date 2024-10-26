from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from telegram.serializers import TelegramConnectionSerializer
from telegram.models import TelegramConnection
from telegram.messages.menu import home_markup
from core.thirdpartyapp.telegram import TelegramUtil

from .bot import telebot_instance, TelegramMessenger

from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt


import telebot
import requests
import logging


logger = logging.getLogger(__name__)


def get_telegram_safe_ips():
    if telegram_ips_cache := cache.get("telegram_safe_ip_list"):
        return telegram_ips_cache

    telegram_ips = requests.get("https://core.telegram.org/bots/webhooks").json()[
        "ip_ranges"
    ]

    cache.set("telegram_safe_ip_list", telegram_ips, 800)

    return telegram_ips


@csrf_exempt
def telebot_respond(request):
    # client_ip = request.META["REMOTE_ADDR"]

    # telegram_ips = get_telegram_safe_ips

    # # Validate the request's IP address against Telegram's IP ranges
    # if client_ip not in telegram_ips:
    #     raise PermissionDenied("Invalid IP address")

    if (
        request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        != settings.TELEGRAM_BOT_API_SECRET
    ):
        raise PermissionDenied("Invalid secret token")

    if request.META["CONTENT_TYPE"] != "application/json":
        raise PermissionDenied

    json_data = request.body.decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    telebot_instance.process_new_updates([update])
    return HttpResponse("")


welcome_text = """*Welcome to Unitap!* 🎉

Your Telegram account is now successfully *connected* to Unitap. From here on, you'll receive important updates, notifications, and can interact with Unitap directly through this chat.

Here’s what you can do:
- *Submit issues or requests*
- *Get notified about events and changes*
- *Ask for hints or help* when needed

Type `/help` at any time to see available commands.

Thanks for joining Unitap! We’re here to assist you in staying productive and connected.
"""


class TelegramLoginCallbackView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TelegramConnectionSerializer

    @property
    def user_profile(self):
        return self.request.user.profile

    def perform_create(self, serializer: TelegramConnectionSerializer):
        telegram_data = serializer.validated_data

        if TelegramUtil().verify_login(telegram_data):
            user_id = telegram_data["id"]

            TelegramMessenger.get_instance().send_message(
                chat_id=user_id, text=welcome_text, reply_markup=home_markup
            )

            serializer.save(user_profile=self.user_profile)
        else:
            return Response({"status": "error"}, status=400)
