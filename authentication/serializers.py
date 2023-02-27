from authentication.models import (
    Profile,
    EVMWallet,
    SolanaWallet,
    BitcoinLightningWallet,
)
from rest_framework import serializers


# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = [
#             "pk",
#             "initial_context_id",
#         ]


class EVMWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = EVMWallet
        fields = [
            "pk",
            "address",
            "added_on",
        ]


class SolanaWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolanaWallet
        fields = [
            "pk",
            "address",
            "added_on",
        ]


class BitcoinLightningWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitcoinLightningWallet
        fields = [
            "pk",
            "address",
            "added_on",
        ]
