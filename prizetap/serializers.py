from rest_framework import serializers

from authentication.serializers import SimpleProfilerSerializer
from core.constraints import ConstraintVerification, get_constraint
from core.serializers import (
    ChainSerializer,
    ConstraintProviderSerializer,
    UserConstraintBaseSerializer,
)

from .constants import CONTRACT_ADDRESSES
from .models import Constraint, LineaRaffleEntries, Raffle, RaffleEntry, UserConstraint


class ConstraintSerializer(UserConstraintBaseSerializer, serializers.ModelSerializer):
    class Meta(UserConstraintBaseSerializer.Meta):
        ref_name = "RaffleConstraint"
        model = Constraint

    def get_params(self, constraint: UserConstraint):
        c_class: ConstraintVerification = get_constraint(constraint.name)
        return [p.name for p in c_class.param_keys()]


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

    class Meta:
        model = RaffleEntry
        fields = [
            "pk",
            "chain",
            "raffle",
            "user_profile",
            "user_wallet_address",
            "created_at",
            "multiplier",
            "tx_hash",
            "claiming_prize_tx",
        ]
        read_only_fields = [
            "pk",
            "chain",
            "raffle",
            "user_profile",
            "user_wallet_address",
            "created_at",
            "multiplier",
        ]

    def get_chain(self, entry: RaffleEntry):
        return entry.raffle.chain.chain_id


class WinnerEntrySerializer(serializers.ModelSerializer):
    user_profile = SimpleProfilerSerializer()

    class Meta:
        model = RaffleEntry
        fields = [
            "pk",
            "user_profile",
            "user_wallet_address",
            "created_at",
            "multiplier",
            "tx_hash",
            "claiming_prize_tx",
        ]
        read_only_fields = [
            "pk",
            "user_profile",
            "user_wallet_address",
            "created_at",
            "multiplier",
        ]


class CreateRaffleSerializer(serializers.ModelSerializer, ConstraintProviderSerializer):
    class Meta:
        model = Raffle
        fields = "__all__"

        read_only_fields = [
            "pk",
            "raffleId",
            "creator_profile",
            "created_at",
            "status",
            "rejection_reason",
            "is_active",
        ]

    def validate(self, data):
        data = super().validate(data)
        if (
            "winners_count" in data
            and data["winners_count"] > data["max_number_of_entries"]
        ):
            raise serializers.ValidationError({"winners_count": "Invalid value"})
        if "is_prize_nft" in data and data["is_prize_nft"] and "nft_ids" not in data:
            raise serializers.ValidationError({"nft_ids": "This field is required"})
        if "nft_ids" in data:
            winners_count = data["winners_count"] if "winners_count" in data else 1
            nft_ids = data["nft_ids"].split(",")
            if winners_count != len(nft_ids):
                raise serializers.ValidationError({"nft_ids": "Invalid value"})
        valid_chains = list(CONTRACT_ADDRESSES.keys())
        chain_id = data["chain"].chain_id
        if chain_id not in valid_chains:
            raise serializers.ValidationError({"chain": "Invalid value"})
        valid_contracts = list(CONTRACT_ADDRESSES[chain_id].values())
        if data["contract"] not in valid_contracts:
            raise serializers.ValidationError({"contract": "Invalid value"})
        data["creator_profile"] = self.context["user_profile"]
        return data

    def create(self, validated_data):
        validated_data = self.save_constraint_files(validated_data)
        return super().create(validated_data)


class RaffleSerializer(serializers.ModelSerializer):
    chain = ChainSerializer()
    winner_entries = WinnerEntrySerializer(many=True, read_only=True)
    user_entry = serializers.SerializerMethodField()
    constraints = serializers.SerializerMethodField()
    creator_profile = SimpleProfilerSerializer()
    is_pre_enrollment = serializers.SerializerMethodField()

    class Meta:
        model = Raffle
        fields = [
            "pk",
            "name",
            "description",
            "necessary_information",
            "creator_name",
            "creator_profile",
            "creator_address",
            "creator_url",
            "discord_url",
            "twitter_url",
            "email_url",
            "telegram_url",
            "image_url",
            "prize_amount",
            "prize_asset",
            "prize_name",
            "prize_symbol",
            "decimals",
            "is_prize_nft",
            "nft_ids",
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
            "status",
            "rejection_reason",
            "tx_hash",
            "is_active",
            "winner_entries",
            "is_expired",
            "is_claimable",
            "is_pre_enrollment",
            "user_entry",
            "number_of_entries",
            "number_of_onchain_entries",
            "max_multiplier",
            "winners_count",
        ]

    def get_constraints(self, raffle: Raffle):
        reversed_constraints = raffle.reversed_constraints_list
        return [
            {
                **ConstraintSerializer(c).data,
                "is_reversed": True if str(c.pk) in reversed_constraints else False,
            }
            for c in raffle.constraints.all()
        ]

    def get_user_entry(self, raffle: Raffle):
        try:
            if not self.context["user"]:
                return None
            return RaffleEntrySerializer(
                raffle.entries.get(user_profile=self.context["user"])
            ).data
        except RaffleEntry.DoesNotExist:
            return None

    def get_is_pre_enrollment(self, raffle: Raffle):
        return bool(raffle.pre_enrollment_wallets)


class LineaRaffleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LineaRaffleEntries
        fields = "__all__"
