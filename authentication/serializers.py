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

    # def update(self, instance, validated_data):
    #     if validated_data.get("primary") is False or instance.wallet_type != "EVM":
    #         raise serializers.ValidationError({"message": "primary must be true or wallet_type must be EVM"})
    #     user_profile = self.context["request"].user.profile
    #     try:
    #         wallet = Wallet.objects.get(user_profile=user_profile, primary=True)
    #         wallet.primary = False
    #         instance.primary = True
    #         Wallet.objects.bulk_update([wallet, instance], ["primary"])
    #         return instance
    #     except Wallet.DoesNotExist:
    #         instance.primary = True
    #         instance.save()
    #         return instance


class ProfileSerializer(serializers.ModelSerializer):
    wallets = WalletSerializer(many=True, read_only=True)
    # total_round_claims_remaining = serializers.SerializerMethodField()
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
            # "total_round_claims_remaining",
            "wallets",
        ]

    def get_token(self, instance):
        token, bol = Token.objects.get_or_create(user=instance.user)
        return token.key

    # def get_total_round_claims_remaining(self, instance):
    #     gs = GlobalSettings.objects.first()
    #     if gs is not None:
    #         return gs.gastap_round_claim_limit - LimitedChainClaimManager.get_total_round_claims(instance)


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
