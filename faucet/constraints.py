from core.constraints import *
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