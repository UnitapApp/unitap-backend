import requests
from core.constraints import *
from core.utils import Web3Utils
from .models import DonationReceipt, Chain, ClaimReceipt

class DonationConstraint(ConstraintVerification):
    _param_keys = [
        ConstraintParam.CHAIN
    ]

    def is_observed(self, *args, **kwargs):
        chain_pk = self._param_values[ConstraintParam.CHAIN]
        return DonationReceipt.objects\
        .filter(chain__pk=chain_pk)\
        .filter(user_profile = self.user_profile)\
        .filter(status=ClaimReceipt.PROCESSED_FOR_TOKENTAP)\
        .exists()
    
class OptimismDonationConstraint(DonationConstraint):
    _param_keys = []

    def is_observed(self, *args, **kwargs):
        try:
            chain = Chain.objects.get(chain_id=10)
        except:
            return False
        self._param_values[ConstraintParam.CHAIN] = chain.pk
        return super().is_observed(*args, **kwargs)

class EvmClaimingGasConstraint(ConstraintVerification):
    _param_keys = [
        ConstraintParam.CHAIN
    ]

    def is_observed(self, *args, **kwargs):
        chain_pk = self._param_values[ConstraintParam.CHAIN]
        chain = Chain.objects.get(pk=chain_pk)
        w3 = Web3Utils(chain.rpc_url_private, chain.poa)
        current_block = w3.current_block()
        user_address = self.user_profile.wallets.get(wallet_type=chain.chain_type).address

        first_internal_tx = requests.get(
            f"{chain.explorer_api_url}/api?module=account&action=txlistinternal&address={user_address}&startblock=0&endblock={current_block}&page=1&offset=1&sort=asc&apikey={chain.explorer_api_key}"
        )
        first_internal_tx = first_internal_tx.json()
        if first_internal_tx and first_internal_tx['status'] == '1':
            first_internal_tx = first_internal_tx['result'][0]
            if first_internal_tx and first_internal_tx['from'] == chain.fund_manager_address.lower()\
                and first_internal_tx['isError'] == '0':
                first_tx = requests.get(
                    f"{chain.explorer_api_url}/api?module=account&action=txlist&address={user_address}&startblock=0&endblock={current_block}&page=1&offset=1&sort=asc&apikey={chain.explorer_api_key}"
                )
                first_tx = first_tx.json()
                if first_tx:
                    if not first_tx['result']:
                        return True
                    first_tx = first_tx['result'][0]
                    claiming_gas_tx = w3.get_transaction_by_hash(first_internal_tx['hash'])
                    web3_first_tx = w3.get_transaction_by_hash(first_tx['hash'])
                    return web3_first_tx['blockNumber'] > claiming_gas_tx['blockNumber']
        return False

class OptimismClaimingGasConstraint(EvmClaimingGasConstraint):
    _param_keys = []

    def is_observed(self, *args, **kwargs):
        try:
            chain = Chain.objects.get(chain_id=10)
        except:
            return False
        self._param_values[ConstraintParam.CHAIN] = chain.pk
        return super().is_observed(*args, **kwargs)