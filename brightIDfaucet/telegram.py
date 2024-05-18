import requests
import time
from collections import defaultdict
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

API_TOKEN = settings.TELEGRAM_API_TOKEN
CHANNEL_ID = settings.TELEGRAM_CHANNEL_ID


BASE_URL = f"https://api.telegram.org/bot{API_TOKEN}"


def send_telegram_log(text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }
    response = requests.post(url, data=payload)
    return response.json()



log_cache = defaultdict(int)
MIN_INTERVAL = 3600


class LogMiddleware(MiddlewareMixin):
    def log_message(self, message):
        log_hash = hash(message)
        current_time = time.time()

        # Check if the log has been sent before or if it has been more than 1 hour
        if current_time - log_cache[log_hash] > MIN_INTERVAL:
            self.send_to_telegram(message)
            log_cache[log_hash] = current_time

    def send_to_telegram(self, message):
        send_telegram_log(message)


