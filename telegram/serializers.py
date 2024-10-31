from rest_framework import serializers

from authentication.serializers import BaseThirdPartyConnectionSerializer
from telegram.models import TelegramConnection


class TelegramConnectionSerializer(BaseThirdPartyConnectionSerializer):
    hash = serializers.CharField(write_only=True)

    class Meta:
        model = TelegramConnection
        fields = "__all__"
        read_only_fields = ["created_at", "pk", "user_profile", "title"]

    def validate_address(self, raise_exception=False):
        return True

    def get_is_connected(self, obj):
        return True
