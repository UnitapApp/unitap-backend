from django.conf import settings

import hashlib
import hmac
import time


def verify_telegram_auth(bot_token, data):
    auth_data = dict(data)
    hash_check = auth_data.pop("hash")

    # Create the data string by sorting keys and concatenating key=value pairs
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(auth_data.items())])

    # Hash the data string with your bot's token
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    # Compare the calculated hash with the received hash
    if calculated_hash != hash_check:
        return False

    # Optional: Check that the authentication data is recent (within a day)
    if time.time() - int(auth_data["auth_date"]) > 86400:
        return False

    return True


class TelegramUtil:
    bot_token = settings.TELEGRAM_BOT_API_KEY
    bot_username = settings.TELEGRAM_BOT_USERNAME

    def __init__(self) -> None:
        pass

    def verify_login(self, telegram_data):
        return verify_telegram_auth(self.bot_token, telegram_data)

    def create_telegram_widget(self, redirect_url):
        telegram_login_widget = create_redirect_login_widget(
            redirect_url, self.bot_username
        )

        return telegram_login_widget
