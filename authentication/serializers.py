from django.db import IntegrityError
from authentication.models import (
    UserProfile,
    Wallet,
)
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from faucet.faucet_manager.claim_manager import LimitedChainClaimManager

from faucet.models import GlobalSettings


class UsernameRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=24)


class AddressRequestSerializer(serializers.Serializer):
    address = serializers.CharField(required=True, max_length=150)


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        pass


# class SetUsernameSerializer(serializers.Serializer):
#     username = UsernameRequestSerializer.username

#     def save(self, user_profile):
#         username = self.validated_data.get("username")

#         try:
#             user_profile.username = username
#             user_profile.save()
#             return {"message": "Username Set"}

#         except IntegrityError:
#             raise ValidationError(
#                 {"message": "This username already exists. Try another one."}
#             )


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
