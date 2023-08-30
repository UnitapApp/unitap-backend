import decimal

from django.db.models import Func, F
from rest_framework import serializers
from rest_framework import status
import web3.exceptions

from authentication.models import UserProfile
from faucet.faucet_manager.claim_manager import LimitedChainClaimManager

from faucet.faucet_manager.credit_strategy import CreditStrategyFactory
from faucet.models import BrightUser, Chain, ClaimReceipt, GlobalSettings, DonationReceipt
from faucet.faucet_manager.fund_manager import EVMFundManager
from core.models import TokenPrice


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
            "tokentap_weekly_claim_limit",
            "prizetap_weekly_claim_limit",
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
            "gas_image_url",
            "max_claim_amount",
            "claimed",
            "unclaimed",
            # "order",
            "total_claims",
            "total_claims_since_last_monday",
            "tokentap_contract_address",
            "needs_funding",
            "is_testnet",
            "chain_type",
            "block_scan_address",
        ]

    def get_claimed(self, chain) -> int:
        user = self.context["request"].user

        if not user.is_authenticated:
            return "N/A"
        user_profile = user.profile
        return CreditStrategyFactory(chain, user_profile).get_strategy().get_claimed()

    def get_unclaimed(self, chain) -> int:
        user = self.context["request"].user

        if not user.is_authenticated:
            return "N/A"
        user_profile = user.profile
        return CreditStrategyFactory(chain, user_profile).get_strategy().get_unclaimed()


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
    chain_name = serializers.CharField(max_length=20, write_only=True)

    def validate(self, attrs):
        chain = self._validate_chain(attrs.pop('chain_name'))
        token_price = self._validate_token_price(chain)
        tx = self._validate_tx_hash(attrs.get('tx_hash'), chain)
        attrs['chain'] = chain
        attrs['value'] = tx.get('value')
        attrs['total_price'] = str(decimal.Decimal(tx.get('value')) * decimal.Decimal(token_price.usd_price))
        return attrs

    def _validate_chain(self, chain_name: str):
        try:
            chain: Chain = Chain.objects.get(chain_name=chain_name, chain_type='EVM')
        except Chain.DoesNotExist:
            raise serializers.ValidationError({'chain': 'chain is not EVM or does not exist.'})

    def _validate_token_price(self, chain: Chain):
        try:
            token_price = TokenPrice.objects.get(symbol=chain.symbol)
        except TokenPrice.DoesNotExist:
            raise serializers.ValidationError({'chain': 'can not found token price for given chain'})
        return token_price

    def _validate_tx_hash(self, tx_hash: str, chain: Chain):
        evm_fund_manage = EVMFundManager(chain)
        user: UserProfile = self.context.get('user')

        try:
            if evm_fund_manage.is_tx_verified(tx_hash) is False:
                raise serializers.ValidationError({'tx_hash': 'tx_hash is not verified'})
            tx = evm_fund_manage.get_tx(tx_hash)
            if evm_fund_manage.to_checksum_address(tx.get('from')) not in user.wallets.annotate(
                    lower_address=Func(F('address'), function='LOWER')).values_list('address', flat=True):
                raise serializers.ValidationError({'tx_hash': 'tx_hash is not from your address'})
            if evm_fund_manage.to_checksum_address(tx.get('to')) != evm_fund_manage.get_fund_manager_checksum_address():
                raise serializers.ValidationError({'tx_hash': 'tx_hash is not to our donation contract address'})
        except web3.exceptions.TransactionNotFound:
            raise serializers.ValidationError({'tx_hash': 'tx_hash not found'})
        except web3.exceptions.TimeExhausted:
            raise serializers.ValidationError({'chain': 'can not connect to chain'},
                                              code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return tx

    class Meta:
        model = DonationReceipt
        depth = 1
        fields = [
            "tx_hash",
            "chain",
            "datetime",
            "total_price",
            "value"
        ]
        read_only_fields = [
            'value',
            'datetime',
            'total_price',
            'chain'
        ]
