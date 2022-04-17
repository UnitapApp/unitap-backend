from rest_framework import serializers

from faucet.faucet_manager.credit_strategy import CreditStrategyFactory
from faucet.models import BrightUser, Chain


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrightUser
        fields = ['pk', 'context_id', "address", "verification_url", "verification_status"]
        read_only_fields = ['context_id']

    def create(self, validated_data):
        address = validated_data['address']
        bright_user = BrightUser.get_or_create(address)
        return bright_user


class ChainSerializer(serializers.ModelSerializer):
    claimed = serializers.SerializerMethodField()
    unclaimed = serializers.SerializerMethodField()

    class Meta:
        model = Chain
        fields = ['pk', 'name', 'symbol', 'chain_id', 'rpc_url',
                  'max_claim_amount',
                  'claimed',
                  'unclaimed',
                  ]

    def get_claimed(self, chain) -> int:
        address = self.context['view'].kwargs.get('address')
        if not address:
            return "N/A"
        bright_user = BrightUser.get_or_create(address)
        return CreditStrategyFactory(chain, bright_user).get_strategy().get_claimed()

    def get_unclaimed(self, chain) -> int:
        address = self.context['view'].kwargs.get('address')
        if not address:
            return "N/A"
        bright_user = BrightUser.get_or_create(address)
        return CreditStrategyFactory(chain, bright_user).get_strategy().get_unclaimed()
