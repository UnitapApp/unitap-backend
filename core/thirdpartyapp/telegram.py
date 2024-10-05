from django_telegram_login.authentication import verify_telegram_authentication
from django_telegram_login.widgets.generator import create_redirect_login_widget

from django.conf import settings


class TelegramUtil:
    bot_token = settings.TELEGRAM_BOT_API_KEY
    bot_username = settings.TELEGRAM_BOT_USERNAME

    def __init__(self) -> None:
        pass

    def login_user(self, telegram_data):
        is_verified = verify_telegram_authentication(
            bot_token=self.bot_token, request_data=telegram_data
        )

    def create_telegram_widget(self, redirect_url):
        telegram_login_widget = create_redirect_login_widget(
            redirect_url, self.bot_username
        )

        return telegram_login_widget
