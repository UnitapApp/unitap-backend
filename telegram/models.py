from typing_extensions import override
from django.db import models
from authentication.models import BaseThirdPartyConnection


class TelegramConnection(BaseThirdPartyConnection):
    title = "Telegram"
    user_id = models.BigIntegerField()
    first_name = models.CharField(null=True, blank=True, max_length=255)
    last_name = models.CharField(null=True, blank=True, max_length=255)
    username = models.CharField(null=True, blank=True, max_length=600)
    # is_collected_easter_egg = models.BooleanField(default=False)

    @override
    def is_connected(self):
        return True

    class Meta:
        permissions = [
            ("can_broadcast", "Can broadcast messages"),
        ]
