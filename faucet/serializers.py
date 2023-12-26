from rest_framework import serializers

from faucet.models import Chain, ClaimReceipt, DonationReceipt, GlobalSettings


class GlobalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = [
            "gastap_round_claim_limit",
            "tokentap_round_claim_limit",
            "prizetap_round_claim_limit",
            "is_gas_tap_available",
        ]


class ChainBalanceSerializer(serializers.ModelSerializer):
    wallet = serializers.SerializerMethodField()
    contract_balance = serializers.SerializerMethodField()
    wallet_balance = serializers.SerializerMethodField()

    class Meta:
        model = Chain
        fields = [
            "pk",
            "chain_name",
            "chain_id",
            "symbol",
            "decimals",
            "needs_funding",
            "has_enough_fees",
            "has_enough_funds",
            "contract_balance",
            "wallet_balance",
            "is_testnet",
            "chain_type",
            "block_scan_address",
            "wallet",
        ]

    def get_wallet(self, chain):
        return chain.wallet.address

    def get_contract_balance(self, chain):
        return chain.manager_balance

    def get_wallet_balance(self, chain):
        return chain.wallet_balance


class SmallChainSerializer(serializers.ModelSerializer):
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
            "gas_image_url",
            "max_claim_amount",
            "is_testnet",
            "tokentap_contract_address",
            "chain_type",
            "block_scan_address",
            "is_one_time_claim",
        ]


class ChainSerializer(serializers.ModelSerializer):
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
            "gas_image_url",
            "max_claim_amount",
            "total_claims",
            "total_claims_this_round",
            "tokentap_contract_address",
            "needs_funding",
            "is_testnet",
            "chain_type",
            "block_scan_address",
            "is_one_time_claim",
        ]


class ReceiptSerializer(serializers.ModelSerializer):
    chain = SmallChainSerializer()

    class Meta:
        model = ClaimReceipt
        fields = [
            "pk",
            "tx_hash",
            "to_address",
            "chain",
            "datetime",
            "amount",
            "status",
            "last_updated",
        ]


class DonationReceiptSerializer(serializers.ModelSerializer):
    chain_pk = serializers.CharField(max_length=20, write_only=True)
    chain = SmallChainSerializer(read_only=True)

    def validate(self, attrs):
        chain = self._validate_chain(attrs.pop("chain_pk"))
        attrs["user_profile"] = self.context.get("user")
        attrs["chain"] = chain
        return attrs

    def _validate_chain(self, pk: str):
        try:
            chain: Chain = Chain.objects.get(pk=pk, chain_type="EVM")
        except Chain.DoesNotExist:
            raise serializers.ValidationError(
                {"chain": "chain is not EVM or does not exist."}
            )
        return chain

    class Meta:
        model = DonationReceipt
        depth = 1
        fields = [
            "tx_hash",
            "chain",
            "datetime",
            "total_price",
            "value",
            "chain_pk",
            "status",
            "user_profile",
        ]
        read_only_fields = [
            "value",
            "datetime",
            "total_price",
            "chain",
            "status",
            "user_profile",
        ]


class LeaderboardSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, read_only=True)
    sum_total_price = serializers.CharField(max_length=150, read_only=True)
    interacted_chains = serializers.ListField(
        child=serializers.IntegerField(), read_only=True
    )
    rank = serializers.IntegerField(read_only=True, required=False)
