from rest_framework import serializers
from core.serializers import UserConstraintBaseSerializer
from authentication.serializers import SimpleProfilerSerializer
from faucet.serializers import SmallChainSerializer
from .models import *
from .constants import *

class ConstraintSerializer(UserConstraintBaseSerializer, serializers.ModelSerializer):
    class Meta(UserConstraintBaseSerializer.Meta):
        ref_name = "RaffleConstraint"
        model = Constraint

    def get_params(self, constraint: UserConstraint):
        c_class: ConstraintVerification = eval(constraint.name)
        return [p.value for p in c_class.param_keys()]

class SimpleRaffleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raffle
        fields = [
            "pk",
            "name",
            "contract",
            "raffleId",
        ]
        read_only_fields = [
            "pk",
            "name",
            "contract",
            "raffleId",
        ]

class RaffleEntrySerializer(serializers.ModelSerializer):
    raffle = SimpleRaffleSerializer()
    user_profile = SimpleProfilerSerializer()
    chain = serializers.SerializerMethodField()
    wallet = serializers.SerializerMethodField()
    class Meta:
        model = RaffleEntry
        fields = [
            "pk",
            "chain",
            "raffle",
            "user_profile",
            "wallet",
            "created_at",
            "multiplier",
            "tx_hash",
            "claiming_prize_tx"
        ]
        read_only_fields = [
            "pk",
            "chain",
            "raffle",
            "user_profile",
            "wallet",
            "created_at",
            "multiplier",
        ]

    def get_chain(self, entry: RaffleEntry):
        return entry.raffle.chain.chain_id
    
    def get_wallet(self, entry: RaffleEntry):
        return entry.user_profile.wallets.get(
            wallet_type=entry.raffle.chain.chain_type).address

class WinnerEntrySerializer(serializers.ModelSerializer):
    user_profile = SimpleProfilerSerializer()
    wallet = serializers.SerializerMethodField()
    class Meta:
        model = RaffleEntry
        fields = [
            "pk",
            "user_profile",
            "wallet",
            "created_at",
            "multiplier",
            "tx_hash",
            "claiming_prize_tx"
        ]
        read_only_fields = [
            "pk",
            "user_profile",
            "wallet",
            "created_at",
            "multiplier",
        ]

    def get_wallet(self, entry: RaffleEntry):
        return entry.user_profile.wallets.get(
            wallet_type=entry.raffle.chain.chain_type).address

class RaffleSerializer(serializers.ModelSerializer):
    chain = SmallChainSerializer()
    winner_entry = WinnerEntrySerializer()
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
            "constraint_params",
            "created_at",
            "start_at",
            "deadline",
            "max_number_of_entries",
            "is_active",
            "winner_entry",
            "is_expired",
            "is_claimable",
            "user_entry",
            "number_of_entries",
            "number_of_onchain_entries",
            "max_multiplier"
        ]
        
    def get_user_entry(self, raffle: Raffle):
        try:
            return RaffleEntrySerializer(
                raffle.entries.get(user_profile=self.context['user'])
            ).data
        except RaffleEntry.DoesNotExist:
            return None
