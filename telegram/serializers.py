from rest_framework import serializers

from authentication.serializers import BaseThirdPartyConnectionSerializer
from telegram.models import TelegramConnection


class TelegramConnectionSerializer(BaseThirdPartyConnectionSerializer):
    hash = serializers.CharField(write_only=True)

    class Meta:
        model = TelegramConnection
        fields = "__all__"
        read_only_fields = [
            "created_on",
            "pk",
            "user_profile",
            "title",
        ]
