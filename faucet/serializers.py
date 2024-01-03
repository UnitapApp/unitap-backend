from rest_framework import serializers

from faucet.models import Chain, ClaimReceipt, DonationReceipt, GlobalSettings

# class UserSerializer(serializers.ModelSerializer):
#     total_weekly_claims_remaining = serializers.SerializerMethodField()

#     class Meta:
#         model = BrightUser
#         fields = [
#             "pk",
#             "context_id",
#             "address",
#             "verification_url",
#             "verification_status",
#             "total_weekly_claims_remaining",
#         ]
#         read_only_fields = ["context_id"]

#     def get_total_weekly_claims_remaining(self, instance):
#         gs = GlobalSettings.objects.first()
#         if gs is not None:
#             return (
#                     gs.weekly_chain_claim_limit
#                     - LimitedChainClaimManager.get_total_weekly_claims(instance)
#             )

#     def create(self, validated_data):
#         address = validated_data["address"]
#         bright_user = BrightUser.objects.get_or_create(address)
#         return bright_user


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
    # claimed = serializers.SerializerMethodField()
    # unclaimed = serializers.SerializerMethodField()

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
            # "claimed",
            # "unclaimed",
            "total_claims",
            "total_claims_this_round",
            "tokentap_contract_address",
            "needs_funding",
            "is_testnet",
            "chain_type",
            "block_scan_address",
            "is_one_time_claim",
        ]


# def get_claimed(self, chain) -> int:
#     user = self.context["request"].user

#     if not user.is_authenticated:
#         return "N/A"
#     user_profile = user.profile
#     return CreditStrategyFactory(chain, user_profile).get_strategy().get_claimed()

# def get_unclaimed(self, chain) -> int:
#     user = self.context["request"].user

#     if not user.is_authenticated:
#         return "N/A"
#     user_profile = user.profile
#     return CreditStrategyFactory(chain, user_profile).get_strategy().get_unclaimed()


class ReceiptSerializer(serializers.ModelSerializer):
    chain = SmallChainSerializer()

    class Meta:
        model = ClaimReceipt
        fields = [
            "pk",
            "tx_hash",
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
    wallet = serializers.CharField(max_length=512, read_only=True)
    rank = serializers.IntegerField(read_only=True, required=False)


class FuelChampionSerializer(serializers.Serializer):
    chain_pk = serializers.CharField(max_length=20, read_only=True)
    username = serializers.CharField(max_length=150, read_only=True)
    donation_amount = serializers.FloatField(read_only=True, required=False)
