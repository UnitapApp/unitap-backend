from rest_framework import serializers
from core.serializers import UserConstraintBaseSerializer
from authentication.serializers import SimpleProfilerSerializer
from faucet.serializers import SmallChainSerializer
from .models import *

class ConstraintSerializer(UserConstraintBaseSerializer, serializers.ModelSerializer):
    class Meta(UserConstraintBaseSerializer.Meta):
        ref_name = "RaffleConstraint"
        model = Constraint
        
class RaffleEntrySerializer(serializers.ModelSerializer):
    user_profile = SimpleProfilerSerializer()
    class Meta:
        model = RaffleEntry
        fields = [
            "pk",
            "user_profile",
            "created_at",
            "signature",
            "multiplier",
            "tx_hash",
            "claiming_prize_tx"
        ]
        read_only_fields = [
            "pk",
            "user_profile",
            "created_at",
            "signature",
            "multiplier",
        ]

    def to_representation(self, instance: RaffleEntry):
        representation = super().to_representation(instance)
        representation["nonce"] = instance.nonce
        return representation

class RaffleSerializer(serializers.ModelSerializer):
    chain = SmallChainSerializer()
    winner_entry = RaffleEntrySerializer()
    user_entry = serializers.SerializerMethodField()
    constraints = ConstraintSerializer(many=True, read_only=True)

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
            "prize_amount",
            "prize_asset",
            "prize_name",
            "prize_symbol",
            "decimals",
            "is_prize_nft",
            "nft_id",
            "token_uri",
            "chain",
            "contract",
            "raffleId",
            "constraints",
            "created_at",
            "deadline",
            "max_number_of_entries",
            "is_active",
            "winner_entry",
            "is_expired",
            "is_claimable",
            "user_entry",
            "number_of_entries",
        ]
        
    def get_user_entry(self, raffle: Raffle):
        try:
            return RaffleEntrySerializer(
                raffle.entries.get(user_profile=self.context['user'])
            ).data
        except RaffleEntry.DoesNotExist:
            return None
