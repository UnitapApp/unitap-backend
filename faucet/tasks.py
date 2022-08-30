from celery import shared_task
from django.db import transaction
from django.db.models import Q

from .models import Chain, ClaimReceipt
from .faucet_manager.fund_manager import EVMFundManager


@shared_task()
def update_receipt_status(receipt_pk):
    try:
        r = ClaimReceipt.objects.get(pk=receipt_pk)
        r.update_status()
    except ClaimReceipt.DoesNotExist:
        pass


@shared_task
def update_pending_receipts_status():  # periodic task
    for _receipt in ClaimReceipt.objects.filter(_status=ClaimReceipt.PENDING):
        update_receipt_status.delay(_receipt.pk)


def has_pending_receipt_with_tx_hash(chain):
    return ClaimReceipt.objects.filter(
        ~Q(tx_hash=None), chain=chain, _status=ClaimReceipt.PENDING
    ).exists()


@shared_task
def proccess_chain_pending_receipts(chain_id):
    with transaction.atomic():
        chain = Chain.objects.select_for_update().get(
            pk=chain_id
        )  # lock based on chain

        # all pending receipts with a tx_hash must be resolved before new transactions can be made
        if has_pending_receipt_with_tx_hash(chain):
            return

        receipts = ClaimReceipt.objects.filter(
            chain=chain, _status=ClaimReceipt.PENDING, tx_hash=None
        )
        if receipts.count() == 0:
            return

        # generate transfer data in batches of 32
        data = [
            {"to": receipt.bright_user.address, "amount": receipt.amount}
            for receipt in receipts[:32]
        ]

        manager = EVMFundManager(chain)
        tx_hash = manager.multi_transfer(data)
        receipts.update(tx_hash=tx_hash)


@shared_task
def process_pending_receipts_with_no_hash():  # periodic task
    for _chain in Chain.objects.all():
        proccess_chain_pending_receipts.delay(_chain.pk)
