import json

from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from authentication.helpers import verify_login_signature
from authentication.models import (  # BaseThirdPartyConnection,
    BrightIDConnection,
    UserProfile,
    Wallet,
)


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
    signature = serializers.CharField(required=True, max_length=256, write_only=True)
    message = serializers.CharField(required=True, max_length=4096, write_only=True)

    class Meta:
        model = Wallet
        fields = ["pk", "wallet_type", "address", "signature", "message"]

    def is_valid(self, raise_exception=False):
        super_is_validated = super().is_valid(raise_exception)

        address = self.validated_data.get("address")
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

    def create(self, validated_data):
        instance = None
        try:
            with transaction.atomic():
                instance = super().create(validated_data)
        except IntegrityError as e:
            try:
                instance = Wallet.objects.deleted_only().get(**validated_data)
            except Wallet.DoesNotExist:
                raise e
            instance.undelete()
        return instance


class BaseThirdPartyConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrightIDConnection
        fields = ["user_profile", "created_at"]


# class BrightIDConnectionSerializer(BaseThirdPartyConnectionSerializer):
#     class Meta(BaseThirdPartyConnectionSerializer.Meta):
#         model = BrightIDConnection
#         fields = BaseThirdPartyConnectionSerializer.Meta.fields + [
#             "context_id",
#         ]


def get_third_party_connection_serializer(connection):
    serializer_class = {
        BrightIDConnection: BaseThirdPartyConnectionSerializer,
        # other mappings for different third-party connection models
    }.get(type(connection), BaseThirdPartyConnectionSerializer)

    return serializer_class(connection)


def thirdparty_connection_serializer(connection_list):
    return [
        get_third_party_connection_serializer(connection).data
        for connection in connection_list
    ]


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
            # "is_aura_verified",
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
