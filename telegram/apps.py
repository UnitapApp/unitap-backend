from django.apps import AppConfig
from django.conf import settings


class TelegramConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telegram"

    def ready(self) -> None:
        if settings.DEPLOYMENT_ENV == "DEV":
            return super().ready()

        from .bot import TelegramMessenger

        messenger = TelegramMessenger.get_instance()
        messenger.ensure_webhook()
        messenger.ready()

        return super().ready()
