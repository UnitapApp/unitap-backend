from celery import shared_task
from django.db import transaction
from django.db.models import Q
from web3.exceptions import TimeExhausted

from .models import Chain, ClaimReceipt, TransactionBatch
from .faucet_manager.fund_manager import EVMFundManager
from sentry_sdk import capture_exception


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
                except EVMFundManager.GasPriceTooHigh:
                    return
                except ValueError:
                    return
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
    # only one onging update per batch

    def save_and_close_batch(_batch):
        _batch.updating = False
        _batch.save()
        _batch.claims.update(_status=batch._status)
        print("closing batch ", _batch.pk)

    with transaction.atomic():
        batch = TransactionBatch.objects.select_for_update().get(pk=batch_pk)
        try:
            if batch.status_should_be_updated:
                print("Updating batch ", batch_pk)
                manager = EVMFundManager(batch.chain)
                if manager.is_tx_verified(batch.tx_hash):
                    batch._status = ClaimReceipt.VERIFIED
                elif batch.is_expired:
                    batch._status = ClaimReceipt.REJECTED
            else:
                print("No need to update batch", batch_pk)

        except TransactionBatch.DoesNotExist:
            capture_exception(e)
        except TimeExhausted as e:
            capture_exception(e)
        except Exception as e:
            save_and_close_batch(batch)
            capture_exception(e)
        finally:
            save_and_close_batch(batch)


@shared_task
def update_pending_batches_with_tx_hash_status():
    batches = TransactionBatch.objects.filter(_status=ClaimReceipt.PENDING).exclude(
        tx_hash=None, updating=True
    )
    batches.update(updating=True)
    print("Updating batches", [b.pk for b in batches])
    for _batch in batches:
        update_pending_batch_with_tx_hash.delay(_batch.pk)


@shared_task
def process_chain_pending_claims(chain_id):
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

        receipts = receipts.order_by("-pk")
        first_receipt_pk = receipts.first().pk
        last_receipt_pk = first_receipt_pk + 32
        receipts = receipts.filter(pk__lt=last_receipt_pk)

        # if there are no pending batches, create a new batch
        batch = TransactionBatch.objects.create(chain=chain)

        # assign the batch to the receipts
        receipts.update(batch=batch)


@shared_task
def process_pending_claims():  # periodic task
    chains = Chain.objects.all()
    for _chain in chains:
        process_chain_pending_claims.delay(_chain.pk)
