from rest_framework import serializers

from faucet.serializers import SmallChainSerializer
from permissions.serializers import PermissionSerializer
from .models import *


class RaffleSerializer(serializers.ModelSerializer):
    chain = SmallChainSerializer()
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Raffle
        fields = [
            "pk",
            "name",
            "description",
            "creator",
            "creator_url",
            "discord_url",
            "twitter_url",
            "image_url",
            "is_prize_nft",
            "prize",
            "chain",
            "contract",
            "raffleId",
            "permissions",
            "created_at",
            "deadline",
            "max_number_of_entries",
            "is_active",
            "winner",
            "is_expired",
            "is_claimable",
            "number_of_entries",
        ]


class RaffleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RaffleEntry
        fields = [
            "pk",
            "user_profile",
            "created_at",
            "signature"
        ]

    def to_representation(self, instance: RaffleEntry):
        representation = super().to_representation(instance)
        representation["nonce"] = instance.nonce
        return representation