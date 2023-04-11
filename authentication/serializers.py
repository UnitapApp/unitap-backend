from authentication.models import (
    UserProfile,
    Wallet,
)
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from faucet.faucet_manager.claim_manager import LimitedChainClaimManager

from faucet.models import GlobalSettings


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            "pk",
            "wallet_type",
            "address",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    wallets = WalletSerializer(many=True, read_only=True)
    total_weekly_claims_remaining = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "pk",
            "token",
            "initial_context_id",
            "is_meet_verified",
            "is_aura_verified",
            "total_weekly_claims_remaining",
            "wallets",
        ]

    def get_token(self, instance):
        token, bol = Token.objects.get_or_create(user=instance.user)
        return token.key

    def get_total_weekly_claims_remaining(self, instance):
        gs = GlobalSettings.objects.first()
        if gs is not None:
            return (
                gs.weekly_chain_claim_limit
                - LimitedChainClaimManager.get_total_weekly_claims(instance)
            )
