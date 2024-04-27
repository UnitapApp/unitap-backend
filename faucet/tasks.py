import logging

from celery import shared_task
from django.core.cache import cache

from core.models import TokenPrice
from core.utils import memcache_lock

from .celery_tasks import CeleryTasks
from .models import ClaimReceipt, DonationReceipt, Faucet, TransactionBatch
from faucet.faucet_manager.claim_manager import RoundCreditStrategy

def passive_address_is_not_none(address):
    if address is not None or address != "" or address != " ":
        return True
    return False


@shared_task(bind=True)
def process_batch(self, batch_pk):
    id_ = f"{self.name}-LOCK-{batch_pk}"
    with memcache_lock(id_, self.app.oid) as acquired:
        if not acquired:
            logging.info("Could not acquire process lock")
            return
        CeleryTasks.process_batch(batch_pk)
        cache.delete(id_)


@shared_task
def process_pending_batches():
    batches = TransactionBatch.objects.filter(
        _status=ClaimReceipt.PENDING, tx_hash=None
    )
    for _batch in batches:
        process_batch.delay(_batch.pk)


@shared_task(bind=True)
def update_pending_batch_with_tx_hash(self, batch_pk):
    # only one ongoing update per batch

    id_ = f"{self.name}-LOCK-{batch_pk}"

    with memcache_lock(id_, self.app.oid) as acquired:
        if not acquired:
            logging.info("Could not acquire update lock")
            return

        CeleryTasks.update_pending_batch_with_tx_hash(batch_pk)

        cache.delete(id_)


@shared_task
def reject_expired_pending_claims():
    CeleryTasks.reject_expired_pending_claims()


@shared_task
def update_pending_batches_with_tx_hash_status():
    batches_queryset = (
        TransactionBatch.objects.filter(_status=ClaimReceipt.PENDING)
        .exclude(tx_hash=None)
        .exclude(updating=True)
    )
    for _batch in batches_queryset:
        update_pending_batch_with_tx_hash.delay(_batch.pk)


@shared_task
def process_faucet_pending_claims(faucet_id):  # locks chain
    CeleryTasks.process_faucet_pending_claims(faucet_id)


@shared_task
def process_pending_claims():  # periodic task
    faucets = Faucet.objects.filter(is_active=True)
    for _faucet in faucets:
        process_faucet_pending_claims.delay(_faucet.pk)


@shared_task
def update_needs_funding_status_faucet(faucet_id):
    CeleryTasks.update_needs_funding_status_faucet(faucet_id)
    CeleryTasks.update_remaining_claim_number(faucet_id)
    CeleryTasks.update_current_fuel_level_faucet(faucet_id)


@shared_task
def update_needs_funding_status():  # periodic task
    faucets = Faucet.objects.filter(is_active=True)
    for _faucet in faucets:
        update_needs_funding_status_faucet.delay(_faucet.pk)


@shared_task
def update_token_price(token_pk):
    CeleryTasks.update_token_price(token_pk)


@shared_task
def update_tokens_price():
    tokens = TokenPrice.objects.exclude(price_url__isnull=True).exclude(price_url="")
    for token in tokens:
        update_token_price.delay(token.pk)


@shared_task(bind=True)
def process_donation_receipt(self, donation_receipt_pk):
    id_ = f"{self.name}-LOCK-{donation_receipt_pk}"
    with memcache_lock(id_, self.app.oid) as acquired:
        if not acquired:
            logging.info("Could not acquire update lock")
            return
        CeleryTasks.process_donation_receipt(donation_receipt_pk)
        cache.delete(id_)


@shared_task
def update_donation_receipt_pending_status():
    """
    update status of pending donation receipt
    """
    pending_donation_receipts = DonationReceipt.objects.filter(
        status=ClaimReceipt.PENDING, faucet__chain__is_active=True
    )
    for pending_donation_receipt in pending_donation_receipts:
        process_donation_receipt.delay(pending_donation_receipt.pk)

@shared_task
def update_claims_count():
    active_faucets = Faucet.objects.filter(is_active=True)
    for faucet in active_faucets:
        total_claims_since_last_round = ClaimReceipt.objects.filter(
            faucet=faucet,
            datetime__gte=RoundCreditStrategy.get_start_of_previous_round(),
            _status__in=[ClaimReceipt.VERIFIED]
        ).count()
        faucet.total_claims_since_last_round = total_claims_since_last_round
        faucet.save()


@shared_task
def update_total_claims_this_round():
    active_faucets = Faucet.objects.filter(is_active=True)
    for faucet in active_faucets:
        print(faucet.total_claims_since_last_round)
        total_claims_this_round = ClaimReceipt.objects.filter(
            faucet=faucet,
            datetime__gte=RoundCreditStrategy.get_start_of_the_round(),
            _status__in=[ClaimReceipt.VERIFIED]
        ).count()
        print(total_claims_this_round)
        faucet.total_claims_this_round = total_claims_this_round
        faucet.save()