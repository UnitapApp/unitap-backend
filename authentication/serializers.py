from authentication.models import (
    UserProfile,
    Wallet,
)
from rest_framework import serializers


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

    class Meta:
        model = UserProfile
        fields = [
            "pk",
            "initial_context_id",
            "is_meet_verified",
            "is_aura_verified",
            "wallets",
        ]

        # TODO add wallets and check verifications should be here or not
