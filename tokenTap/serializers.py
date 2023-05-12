from faucet.serializers import SmallChainSerializer
from rest_framework import serializers
from permissions.serializers import PermissionSerializer
from tokenTap.models import TokenDistribution


class TokenDistributionSerializer(serializers.ModelSerializer):
    chain = SmallChainSerializer()
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = TokenDistribution
        fields = [
            "id",
            "name",
            "distributer",
            "distributer_url",
            "discord_url",
            "twitter_url",
            "image_url",
            "token",
            "token_address",
            "amount",
            "chain",
            "permissions",
            "created_at",
            "deadline",
            "max_number_of_claims",
            "notes",
            "is_expired",
            "is_maxed_out",
            "is_claimable",
        ]
