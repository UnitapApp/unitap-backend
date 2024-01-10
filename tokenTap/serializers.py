import base64
import json

from rest_framework import serializers

from core.constraints import ConstraintVerification, get_constraint
from core.serializers import ChainSerializer, UserConstraintBaseSerializer
from tokenTap.models import (
    Constraint,
    TokenDistribution,
    TokenDistributionClaim,
    UserConstraint,
)

from .constants import CONTRACT_ADDRESSES


class ConstraintSerializer(UserConstraintBaseSerializer, serializers.ModelSerializer):
    class Meta(UserConstraintBaseSerializer.Meta):
        ref_name = "TokenDistributionConstraint"
        model = Constraint

    def get_params(self, constraint: UserConstraint):
        c_class: ConstraintVerification = get_constraint(constraint.name)
        return [p.name for p in c_class.param_keys()]


class DetailResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        pass


class TokenDistributionSerializer(serializers.ModelSerializer):
    chain = ChainSerializer()
    constraints = ConstraintSerializer(many=True)

    class Meta:
        model = TokenDistribution
        fields = [
            "id",
            "name",
            "distributor",
            "distributor_url",
            "discord_url",
            "twitter_url",
            "email_url",
            "telegram_url",
            "image_url",
            "token_image_url",
            "token",
            "token_address",
            "amount",
            "chain",
            "contract",
            "constraints",
            "created_at",
            "start_at",
            "deadline",
            "max_number_of_claims",
            "number_of_claims",
            "total_claims_since_last_round",
            "notes",
            "necessary_information",
            "status",
            "rejection_reason",
            "is_active",
            "is_expired",
            "is_maxed_out",
            "is_claimable",
        ]


class SmallTokenDistributionSerializer(serializers.ModelSerializer):
    chain = ChainSerializer()
    constraints = ConstraintSerializer(many=True)

    class Meta:
        model = TokenDistribution
        fields = [
            "id",
            "name",
            "distributor",
            "distributor_url",
            "discord_url",
            "twitter_url",
            "image_url",
            "token",
            "token_address",
            "amount",
            "chain",
            "contract",
            "constraints",
            "created_at",
            "deadline",
            "max_number_of_claims",
            "notes",
            "token_image_url",
        ]


class PayloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenDistributionClaim
        fields = ["user_wallet_address", "token", "amount", "nonce", "signature"]


class TokenDistributionClaimSerializer(serializers.ModelSerializer):
    token_distribution = SmallTokenDistributionSerializer()
    payload = serializers.SerializerMethodField()

    class Meta:
        model = TokenDistributionClaim
        fields = [
            "id",
            "token_distribution",
            "user_profile",
            "user_wallet_address",
            "created_at",
            "payload",
            "status",
            "tx_hash",
        ]

    def get_payload(self, obj):
        return PayloadSerializer(obj).data


class TokenDistributionClaimResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    signature = TokenDistributionClaimSerializer()


class CreateTokenDistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenDistribution
        fields = "__all__"

        read_only_fields = [
            "pk",
            "distributor_profile",
            "created_at",
            "status",
            "rejection_reason",
            "is_active",
        ]

    def validate(self, data):
        constraints = data["constraints"]
        constraint_params = json.loads(base64.b64decode(data["constraint_params"]))
        data["constraint_params"] = base64.b64decode(data["constraint_params"]).decode(
            "utf-8"
        )
        reversed_constraints = []
        if "reversed_constraints" in data:
            reversed_constraints = str(data["reversed_constraints"]).split(",")
        if len(constraints) != 0:
            for c in constraints:
                constraint_class: ConstraintVerification = get_constraint(c.name)
                try:
                    if len(constraint_class.param_keys()) != 0:
                        constraint_class.is_valid_param_keys(constraint_params[c.name])
                except KeyError as e:
                    raise serializers.ValidationError(
                        {"constraint_params": [{f"{c.name}": str(e)}]}
                    )
        valid_constraints = [str(c.pk) for c in constraints]
        if len(reversed_constraints) > 0:
            for c in reversed_constraints:
                if c not in valid_constraints:
                    raise serializers.ValidationError(
                        {"reversed_constraints": [{f"{c}": "Invalid constraint pk"}]}
                    )
        valid_chains = list(CONTRACT_ADDRESSES.keys())
        chain_id = data["chain"].chain_id
        if chain_id not in valid_chains:
            raise serializers.ValidationError({"chain": "Invalid value"})
        valid_contracts = list(CONTRACT_ADDRESSES[chain_id].values())
        if data["contract"] not in valid_contracts:
            raise serializers.ValidationError({"contract": "Invalid value"})
        data["distributor_profile"] = self.context["user_profile"]
        return data
