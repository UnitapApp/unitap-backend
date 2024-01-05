import json

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from authentication.helpers import verify_login_signature
from authentication.models import UserProfile, Wallet


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


class WalletSerializer(serializers.ModelSerializer):
    signature = serializers.CharField(required=True, max_length=150, write_only=True)
    message = serializers.CharField(required=True, max_length=150, write_only=True)

    class Meta:
        model = Wallet
        fields = ["pk", "wallet_type", "wallet_address", "signature", "message"]

    def is_valid(self, raise_exception=False):
        super_is_validated = super().is_valid(raise_exception)

        address = self.validated_data.get("wallet_address")
        message = self.validated_data.get("message")
        signature = self.validated_data.get("signature")

        signature_is_valid = verify_login_signature(
            address, json.loads(message), signature
        )

        if not signature_is_valid and raise_exception:
            raise serializers.ValidationError("Signature is not valid")

        self.validated_data.pop("signature", None)
        self.validated_data.pop("message", None)

        return super_is_validated and signature_is_valid


class ProfileSerializer(serializers.ModelSerializer):
    wallets = WalletSerializer(many=True, read_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "pk",
            "username",
            "token",
            "is_meet_verified",
            "is_aura_verified",
            "wallets",
        ]

    def get_token(self, instance):
        token, bol = Token.objects.get_or_create(user=instance.user)
        return token.key


class SimpleProfilerSerializer(serializers.ModelSerializer):
    wallets = WalletSerializer(many=True, read_only=True)
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "pk",
            "username",
            "wallets",
        ]

    def get_username(self, user_profile: UserProfile):
        if not user_profile.username:
            return f"User{user_profile.pk}"
        return user_profile.username


class UserHistoryCountSerializer(serializers.Serializer):
    gas_claim = serializers.IntegerField()
    token_claim = serializers.IntegerField()
    raffle_win = serializers.IntegerField()
