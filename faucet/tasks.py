from celery import shared_task
from django.db import transaction
from .models import Chain, BrightUser, ClaimReceipt
from .faucet_manager.fund_manager import EVMFundManager


@shared_task
def broadcast_and_wait_for_receipt(chain_id, bright_user_id, pending_receipt_id, amount):
    with transaction.atomic():
        chain = Chain.objects.select_for_update().get(pk=chain_id)  # lock based on chain

        bright_user = BrightUser.objects.get(pk=bright_user_id)
        pending_receipt = ClaimReceipt.objects.get(pk=pending_receipt_id)

        manager = EVMFundManager(chain)
        receipt = manager.transfer(bright_user, pending_receipt, amount)
        manager.update_receipt_status(receipt)
        return receipt
