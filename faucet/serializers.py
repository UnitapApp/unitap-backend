from rest_framework import serializers
from faucet.faucet_manager.claim_manager import LimitedChainClaimManager

from faucet.faucet_manager.credit_strategy import CreditStrategyFactory
from faucet.models import BrightUser, Chain, ClaimReceipt, GlobalSettings


class UserSerializer(serializers.ModelSerializer):

    total_weekly_claims_remaining = serializers.SerializerMethodField()

    class Meta:
        model = BrightUser
        fields = [
            "pk",
            "context_id",
            "address",
            "verification_url",
            "verification_status",
            "total_weekly_claims_remaining",
        ]
        read_only_fields = ["context_id"]

    def get_total_weekly_claims_remaining(self, instance):
        gs = GlobalSettings.objects.first()
        if gs is not None:
            return (
                gs.weekly_chain_claim_limit
                - LimitedChainClaimManager.get_total_weekly_claims(instance)
            )

    def create(self, validated_data):
        address = validated_data["address"]
        bright_user = BrightUser.objects.get_or_create(address)
        return bright_user


class GlobalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = [
            "weekly_chain_claim_limit",
        ]


class ChainSerializer(serializers.ModelSerializer):
    claimed = serializers.SerializerMethodField()
    unclaimed = serializers.SerializerMethodField()

    class Meta:
        model = Chain
        fields = [
            "pk",
            "chain_name",
            "chain_id",
            "fund_manager_address",
            "native_currency_name",
            "symbol",
            "decimals",
            "explorer_url",
            "rpc_url",
            "logo_url",
            "modal_url",
            "max_claim_amount",
            "claimed",
            "unclaimed",
            "order",
            "total_claims",
            "total_claims_since_last_monday",
            "is_gas_price_too_high",
            "gas_price",
        ]

    def get_claimed(self, chain) -> int:
        address = self.context["view"].kwargs.get("address")
        if not address:
            return "N/A"
        bright_user = BrightUser.objects.get_or_create(address)
        return CreditStrategyFactory(chain, bright_user).get_strategy().get_claimed()

    def get_unclaimed(self, chain) -> int:
        address = self.context["view"].kwargs.get("address")
        if not address:
            return "N/A"
        bright_user = BrightUser.objects.get_or_create(address)
        return CreditStrategyFactory(chain, bright_user).get_strategy().get_unclaimed()


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimReceipt
        fields = ["pk", "tx_hash", "chain", "datetime", "amount", "status"]
