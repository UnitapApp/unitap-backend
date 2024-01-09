from rest_framework import serializers

from core.serializers import ChainSerializer
from faucet.models import ClaimReceipt, DonationReceipt, Faucet, GlobalSettings


class GlobalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = [
            "gastap_round_claim_limit",
            "tokentap_round_claim_limit",
            "prizetap_round_claim_limit",
            "is_gas_tap_available",
        ]


class FaucetBalanceSerializer(serializers.ModelSerializer):
    contract_balance = serializers.SerializerMethodField()
    wallet_balance = serializers.SerializerMethodField()
    chain = ChainSerializer()
    get_has_enough_fees = serializers.SerializerMethodField()
    get_wallet_address = serializers.SerializerMethodField()

    class Meta:
        model = Faucet
        fields = [
            "pk",
            "chain",
            "needs_funding",
            "has_enough_funds",
            "get_has_enough_fees",
            "contract_balance",
            "wallet_balance",
            "fund_manager_address",
            "get_wallet_address",
            "block_scan_address",
        ]

    def get_contract_balance(self, faucet):
        return faucet.manager_balance

    def get_wallet_balance(self, faucet):
        return faucet.chain.wallet_balance

    def get_has_enough_fees(self, faucet):
        return faucet.chain.has_enough_fees

    def get_wallet_address(self, faucet):
        return faucet.chain.wallet.address


class SmallFaucetSerializer(serializers.ModelSerializer):
    chain = ChainSerializer()

    class Meta:
        model = Faucet
        fields = [
            "pk",
            "chain",
            "fund_manager_address",
            "gas_image_url",
            "max_claim_amount",
            "tokentap_contract_address",
            "block_scan_address",
            "is_one_time_claim",
        ]


class FaucetSerializer(serializers.ModelSerializer):
    chain = ChainSerializer()

    class Meta:
        model = Faucet
        fields = [
            "pk",
            "chain",
            "fund_manager_address",
            "gas_image_url",
            "max_claim_amount",
            "total_claims",
            "total_claims_this_round",
            "tokentap_contract_address",
            "needs_funding",
            "block_scan_address",
            "is_one_time_claim",
        ]


class ReceiptSerializer(serializers.ModelSerializer):
    faucet = SmallFaucetSerializer()

    class Meta:
        model = ClaimReceipt
        fields = [
            "pk",
            "tx_hash",
            "to_address",
            "faucet",
            "datetime",
            "amount",
            "status",
            "last_updated",
        ]


class DonationReceiptSerializer(serializers.ModelSerializer):
    faucet_pk = serializers.CharField(max_length=20, write_only=True)
    faucet = FaucetSerializer(read_only=True)

    def validate(self, attrs):
        faucet = self._validate_faucet(attrs.pop("faucet_pk"))
        attrs["user_profile"] = self.context.get("user")
        attrs["faucet"] = faucet
        return attrs

    def _validate_faucet(self, pk: str):
        try:
            faucet: Faucet = Faucet.objects.get(pk=pk, chain__chain_type="EVM")
        except Faucet.DoesNotExist:
            raise serializers.ValidationError(
                {"faucet": "faucet is not EVM or does not exist."}
            )
        return faucet

    class Meta:
        model = DonationReceipt
        depth = 1
        fields = [
            "tx_hash",
            "faucet",
            "datetime",
            "total_price",
            "value",
            "faucet_pk",
            "status",
            "user_profile",
        ]
        read_only_fields = [
            "value",
            "datetime",
            "total_price",
            "faucet",
            "status",
            "user_profile",
        ]


class LeaderboardSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, read_only=True)
    sum_total_price = serializers.CharField(max_length=150, read_only=True)
    interacted_chains = serializers.ListField(
        child=serializers.IntegerField(), read_only=True
    )
    wallet = serializers.CharField(max_length=512, read_only=True)
    rank = serializers.IntegerField(read_only=True, required=False)


class FuelChampionSerializer(serializers.Serializer):
    faucet_pk = serializers.CharField(max_length=20, read_only=True)
    username = serializers.CharField(max_length=150, read_only=True)
