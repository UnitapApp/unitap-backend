from authentication.models import (
    UserProfile,
    Wallet,
)
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "pk",
            "initial_context_id",
            "is_meet_verified",
            "is_aura_verified",
        ]

        # TODO add wallets and check verifications should be here or not


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            "pk",
            "wallet_type",
            "address",
        ]
