from rest_framework import serializers

from faucet.serializers import SmallChainSerializer
from .models import *


class RaffleSerializer(serializers.ModelSerializer):
    chain = SmallChainSerializer()
    winner = serializers.SerializerMethodField()
    user_entry = serializers.SerializerMethodField()

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
            "created_at",
            "deadline",
            "max_number_of_entries",
            "is_active",
            "winner",
            "is_expired",
            "is_claimable",
            "user_entry",
            "number_of_entries",
        ]

    def get_winner(self, raffle: Raffle):
        if raffle.winner:
            return raffle.winner.pk
        
    def get_user_entry(self, raffle: Raffle):
        try:
            return RaffleEntrySerializer(
                raffle.entries.get(user_profile=self.context['user'])
            ).data
        except RaffleEntry.DoesNotExist:
            return None



class RaffleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RaffleEntry
        fields = [
            "pk",
            "user_profile",
            "created_at",
            "signature",
            "tx_hash"
        ]
        read_only_fields = [
            "pk",
            "user_profile",
            "created_at",
            "signature"
        ]

    def to_representation(self, instance: RaffleEntry):
        representation = super().to_representation(instance)
        representation["nonce"] = instance.nonce
        return representation