from core.constraints.abstract import ConstraintParam, ConstraintVerification
from core.utils import Web3Utils, InvalidAddressException
from rest_framework.exceptions import ValidationError
from django.conf import settings


class GLMStakingVerification(ConstraintVerification):
    _param_keys = [
        ConstraintParam.CHAIN,
        ConstraintParam.MINIMUM,
    ]

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs):
        from core.models import Chain

        chain_pk = self.param_values[ConstraintParam.CHAIN.name]
        
        minimum = self.param_values[ConstraintParam.MINIMUM.name]

        chain = Chain.objects.get(pk=chain_pk)
        web3_utils = Web3Utils(chain.rpc_url_private, chain.poa)

        user_wallets = self.user_profile.wallets.filter(wallet_type=chain.chain_type)

        staked_amount = 0
        try:
            for wallet in user_wallets:
                staked_amount += self.get_staked_amount(wallet.address, web3_utils) / 10 ** 18
                
        except InvalidAddressException as e:
            raise ValidationError({"address": str(e)})
        
        return staked_amount >= int(minimum)

    def get_staked_amount(self, user_address: str, web3_utils: Web3Utils) -> int:
        abi = '[{"inputs":[{"internalType":"address","name":"glmAddress","type":"address"},{"internalType":"address","name":"_auth","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"depositBefore","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"when","type":"uint256"},{"indexed":false,"internalType":"address","name":"user","type":"address"}],"name":"Locked","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"depositBefore","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"when","type":"uint256"},{"indexed":false,"internalType":"address","name":"user","type":"address"}],"name":"Unlocked","type":"event"},{"inputs":[],"name":"auth","outputs":[{"internalType":"contract Auth","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"deposits","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"glm","outputs":[{"internalType":"contract ERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"lock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"unlock","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
        web3_utils.set_contract(settings.GLM_CONTRACT_ADDRESS, abi)
        deposits_function = web3_utils.contract.functions.deposits(user_address)
        return web3_utils.contract_call(deposits_function)

