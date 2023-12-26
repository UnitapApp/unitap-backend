from rest_framework import serializers
from rest_framework.authtoken.models import Token

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
    class Meta:
        model = Wallet
        fields = ["pk", "wallet_type", "address"]


class ProfileSerializer(serializers.ModelSerializer):
    wallets = WalletSerializer(many=True, read_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "pk",
            "username",
            "token",
            "initial_context_id",
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
