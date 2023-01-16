from celery import shared_task
from django.db import transaction
from django.db.models import Q
from web3.exceptions import TimeExhausted

from .models import Chain, ClaimReceipt, TransactionBatch
from .faucet_manager.fund_manager import EVMFundManager
from sentry_sdk import capture_exception
from django.utils import timezone


def has_pending_batch(chain):
    return TransactionBatch.objects.filter(
        chain=chain, _status=ClaimReceipt.PENDING
    ).exists()


@shared_task
def process_batch(batch_pk):
    """
    Process a batch of claims and send the funds to the users
    creates an on-chain transaction
    """
    try:
        with transaction.atomic():
            batch = TransactionBatch.objects.select_for_update().get(pk=batch_pk)

            if batch.is_expired:
                batch._status = ClaimReceipt.REJECTED
                batch.save()
                batch.claims.update(_status=batch._status)
                return

            if batch.should_be_processed:
                data = [
                    {"to": receipt.bright_user.address, "amount": receipt.amount}
                    for receipt in batch.claims.all()
                ]

                manager = EVMFundManager(batch.chain)

                try:
                    tx_hash = manager.multi_transfer(data)
                    batch.tx_hash = tx_hash
                    batch.save()
                except:
                    capture_exception()
    except TransactionBatch.DoesNotExist:
        pass


@shared_task
def proccess_pending_batches():
    batches = TransactionBatch.objects.filter(
        _status=ClaimReceipt.PENDING, tx_hash=None
    )
    for _batch in batches:
        process_batch.delay(_batch.pk)


@shared_task
def update_pending_batch_with_tx_hash(batch_pk):
    # only one on going update per batch

    def save_and_close_batch(_batch):
        _batch.updating = False
        _batch.save()
        _batch.claims.update(_status=batch._status)

    with transaction.atomic():
        batch = TransactionBatch.objects.select_for_update().get(pk=batch_pk)
        try:
            if batch.status_should_be_updated:
                manager = EVMFundManager(batch.chain)

                if manager.is_tx_verified(batch.tx_hash):
                    batch._status = ClaimReceipt.VERIFIED
                elif batch.is_expired:
                    batch._status = ClaimReceipt.REJECTED
        except:
            if batch.is_expired:
                batch._status = ClaimReceipt.REJECTED
            capture_exception()
        finally:
            save_and_close_batch(batch)


@shared_task
def reject_expired_pending_claims():
    ClaimReceipt.objects.filter(
        batch=None,
        _status=ClaimReceipt.PENDING,
        datetime__lte=timezone.now()
        - timezone.timedelta(minutes=ClaimReceipt.MAX_PENDING_DURATION),
    ).update(_status=ClaimReceipt.REJECTED)


@shared_task
def clear_updating_status():
    TransactionBatch.objects.filter(updating=True).update(updating=False)


@shared_task
def update_pending_batches_with_tx_hash_status():
    batches_queryset = (
        TransactionBatch.objects.filter(_status=ClaimReceipt.PENDING)
        .exclude(tx_hash=None)
        .exclude(updating=True)
    )
    batches = list(batches_queryset)
    batches_queryset.update(updating=True)
    for _batch in batches:
        update_pending_batch_with_tx_hash.delay(_batch.pk)


@shared_task
def process_chain_pending_claims(chain_id):  # locks chain
    with transaction.atomic():
        chain = Chain.objects.select_for_update().get(
            pk=chain_id
        )  # lock based on chain

        # all pending batches must be resolved before new transactions can be made
        if has_pending_batch(chain):
            return

        # get all pending receipts for this chain
        # pending receipts are receipts that have not been batched yet
        receipts = ClaimReceipt.objects.filter(
            chain=chain, _status=ClaimReceipt.PENDING, batch=None
        )

        if receipts.count() == 0:
            return

        receipts = receipts.order_by("pk")[:32]

        # if there are no pending batches, create a new batch
        batch = TransactionBatch.objects.create(chain=chain)

        # assign the batch to the receipts
        for receipt in receipts:
            receipt.batch = batch
            receipt.save()


@shared_task
def process_pending_claims():  # periodic task
    chains = Chain.objects.filter(is_active=True)
    for _chain in chains:
        process_chain_pending_claims.delay(_chain.pk)


@shared_task
def update_needs_funding_status_chain(chain_id):

    try:
        chain = Chain.objects.get(pk=chain_id)
        # if has enough funds and enough fees, needs_funding is False

        chain.needs_funding = True

        if chain.has_enough_funds and chain.has_enough_fees:
            chain.needs_funding = False

        chain.save()
    except:
        capture_exception()


@shared_task
def update_needs_funding_status():  # periodic task
    chains = Chain.objects.all()
    for _chain in chains:
        update_needs_funding_status_chain.delay(_chain.pk)
