from django.db.models import Sum

from faucet.models import ClaimReceipt


class SimpleCreditStrategy:

    def __init__(self, chain, bright_user):
        self.chain = chain
        self.bright_user = bright_user

    def get_claim_receipts(self):
        return ClaimReceipt.objects.filter(chain=self.chain, bright_user=self.bright_user)

    def get_claimed(self):
        aggregate = self.get_claim_receipts().aggregate(Sum("amount"))
        _sum = aggregate.get('amount__sum')
        if not _sum:
            return 0
        return _sum
