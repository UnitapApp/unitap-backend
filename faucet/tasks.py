import time
import logging
import decimal
from contextlib import contextmanager
import web3.exceptions
import requests
from celery import shared_task
from django.core.cache import cache
from django.db import transaction
from django.db.models import F, Func
from django.utils import timezone
from sentry_sdk import capture_exception
from authentication.models import NetworkTypes, Wallet
from tokenTap.models import TokenDistributionClaim
from django.conf import settings as django_settings
from .faucet_manager.fund_manager import (
    EVMFundManager,
    SolanaFundManager,
    LightningFundManager,
    FundMangerException,
)
from core.models import TokenPrice
from .models import Chain, ClaimReceipt, TransactionBatch, DonationReceipt


@contextmanager
def memcache_lock(lock_id, oid, lock_expire=60):
    timeout_at = time.monotonic() + lock_expire
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, lock_expire)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


def has_pending_batch(chain):
    return TransactionBatch.objects.filter(
        chain=chain, _status=ClaimReceipt.PENDING
    ).exists()


def passive_address_is_not_none(address):
    if address is not None or address != "" or address != " ":
        return True
    return False


@shared_task(bind=True)
def process_batch(self, batch_pk):
    """
    Process a batch of claims and send the funds to the users
    creates an on-chain transaction
    """

    id = f"{self.name}-LOCK-{batch_pk}"

    try:
        with memcache_lock(id, self.app.oid) as acquired:
            if not acquired:
                print("Could not acquire process lock")
                return

            print(f"Processing Batch {batch_pk}")

            batch = TransactionBatch.objects.get(pk=batch_pk)

            if batch.should_be_processed:
                if batch.is_expired:
                    batch._status = ClaimReceipt.REJECTED
                    batch.save()
                    batch.claims.update(_status=batch._status)
                    return

                data = [
                    {
                        "to": receipt.passive_address
                        if receipt.passive_address is not None
                        else Wallet.objects.get(
                            user_profile=receipt.user_profile,
                            wallet_type=batch.chain.chain_type,
                        ).address,
                        "amount": int(receipt.amount),
                    }
                    for receipt in batch.claims.all()
                ]
                #####
                print(data)

                try:
                    if batch.chain.chain_type == NetworkTypes.SOLANA:
                        manager = SolanaFundManager(batch.chain)
                    elif batch.chain.chain_type == NetworkTypes.LIGHTNING:
                        manager = LightningFundManager(batch.chain)
                    elif (
                            batch.chain.chain_type == NetworkTypes.EVM
                            or batch.chain.chain_type == NetworkTypes.NONEVMXDC
                    ):
                        manager = EVMFundManager(batch.chain)
                    else:
                        raise Exception(
                            f"Invalid chain type to process batch, chain type {batch.chain.chain_type}"
                        )
                    tx_hash = manager.multi_transfer(data)
                    batch.tx_hash = tx_hash
                    batch.save()
                except FundMangerException.GasPriceTooHigh as e:
                    logging.error(e)
                except FundMangerException.RPCError as e:
                    logging.error(e)
                except Exception as e:
                    capture_exception()
                    print(str(e))

            cache.delete(id)
    except TransactionBatch.DoesNotExist:
        pass


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

    id = f"{self.name}-LOCK-{batch_pk}"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print("Could not acquire update lock")
            return

        print("Updating Batch")

        batch = TransactionBatch.objects.get(pk=batch_pk)
        try:
            if batch.status_should_be_updated:
                if batch.chain.chain_type == NetworkTypes.SOLANA:
                    manager = SolanaFundManager(batch.chain)
                elif batch.chain.chain_type == NetworkTypes.LIGHTNING:
                    manager = LightningFundManager(batch.chain)
                elif (
                        batch.chain.chain_type == NetworkTypes.EVM
                        or batch.chain.chain_type == NetworkTypes.NONEVMXDC
                ):
                    manager = EVMFundManager(batch.chain)
                else:
                    raise Exception(
                        f"Invalid chain type to update pending batch, chain type {batch.chain.chain_type}"
                    )

                if manager.is_tx_verified(batch.tx_hash):
                    batch._status = ClaimReceipt.VERIFIED
                elif batch.is_expired:
                    batch._status = ClaimReceipt.REJECTED
        except Exception as e:
            if batch.is_expired:
                batch._status = ClaimReceipt.REJECTED
            capture_exception()
            print(str(e))
        finally:
            batch.save()
            batch.claims.update(_status=batch._status)

        cache.delete(id)


@shared_task
def reject_expired_pending_claims():
    ClaimReceipt.objects.filter(
        batch=None,
        _status=ClaimReceipt.PENDING,
        datetime__lte=timezone.now()
                      - timezone.timedelta(minutes=ClaimReceipt.MAX_PENDING_DURATION),
    ).update(_status=ClaimReceipt.REJECTED)


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

        if chain.chain_type == NetworkTypes.LIGHTNING:
            receipts = receipts.order_by("pk")[:1]
        else:
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
    chains = Chain.objects.filter(is_active=True)
    for _chain in chains:
        update_needs_funding_status_chain.delay(_chain.pk)


@shared_task
def process_verified_lighning_claim(gas_tap_claim_id):
    try:
        claim = ClaimReceipt.objects.get(pk=gas_tap_claim_id)
        user_profile = claim.user_profile
        tokentap_lightning_claim = (
            TokenDistributionClaim.objects.filter(
                user_profile=user_profile,
                token_distribution__chain__chain_type=NetworkTypes.LIGHTNING,
            )
            .order_by("-created_at")
            .first()
        )

        if not tokentap_lightning_claim:
            raise Exception("No tokentap claim found for user")

        tokentap_lightning_claim.status = ClaimReceipt.VERIFIED
        tokentap_lightning_claim.tx_hash = claim.tx_hash
        tokentap_lightning_claim.save()

        claim._status = ClaimReceipt.PROCESSED_FOR_TOKENTAP
        claim.save()

    except Exception as e:
        capture_exception()
        print(f"error in processing lightning claims: {str(e)}")


@shared_task
def process_rejected_lighning_claim(gas_tap_claim_id):
    try:
        claim = ClaimReceipt.objects.get(pk=gas_tap_claim_id)
        user_profile = claim.user_profile
        tokentap_lightning_claim = (
            TokenDistributionClaim.objects.filter(
                user_profile=user_profile,
                token_distribution__chain__chain_type=NetworkTypes.LIGHTNING,
            )
            .order_by("-created_at")
            .first()
        )

        if not tokentap_lightning_claim:
            raise Exception("No tokentap claim found for user")

        tokentap_lightning_claim.delete()

        claim._status = ClaimReceipt.PROCESSED_FOR_TOKENTAP_REJECT
        claim.save()

    except Exception as e:
        capture_exception()
        print(f"error in processing lightning claims: {str(e)}")


@shared_task
def update_tokentap_claim_for_verified_lightning_claims():
    claims = ClaimReceipt.objects.filter(
        _status__in=[ClaimReceipt.VERIFIED, ClaimReceipt.REJECTED],
        chain__chain_type=NetworkTypes.LIGHTNING,
    )
    for _claim in claims:
        if django_settings.IS_TESTING:
            if _claim._status == ClaimReceipt.VERIFIED:
                process_verified_lighning_claim.apply((_claim.pk,))
            elif _claim._status == ClaimReceipt.REJECTED:
                process_rejected_lighning_claim.apply((_claim.pk,))
        else:
            if _claim._status == ClaimReceipt.VERIFIED:

                process_verified_lighning_claim.delay(
                    _claim.pk,
                )
            elif _claim._status == ClaimReceipt.REJECTED:
                process_rejected_lighning_claim.delay(
                    _claim.pk,
                )


@shared_task
def update_tokens_price():
    """
    update token.usd_price for all TokenPrice records in DB
    """

    # TODO: we can make this function performance better by using aiohttp and asyncio or Threads
    tokens = TokenPrice.objects.exclude(price_url__isnull=True)
    res_gen = map(lambda token: (token, requests.get(token.price_url, timeout=5)), tokens)

    def parse_request(token: TokenPrice, request_res: requests.Response):
        try:
            request_res.raise_for_status()
            json_data = request_res.json()
            token.usd_price = json_data['data']['rates']['USD']
            # TODO: save all change when this function ended for all url done for better performance
            token.save()
        except requests.HTTPError as e:
            logging.exception(
                f'requests for url: {request_res.url} can not fetched with status_code: {request_res.status_code}. \
                {str(e)}')

        except KeyError as e:
            logging.exception(
                f'requests for url: {request_res.url} data do not have property keys for loading data. {str(e)}')

        except Exception as e:
            logging.exception(f'requests for url: {request_res.url} got error {type(e).__name__}. {str(e)}')

    [parse_request(*res) for res in res_gen]


@shared_task(bind=True)
def process_donation_receipt(self, donation_receipt_pk):
    lock_name = f'{self.name}-LOCK-{donation_receipt_pk}'
    logging.info(f'lock name is: {lock_name}')
    with memcache_lock(lock_name, self.app.oid) as acquired:
        donation_receipt = DonationReceipt.objects.get(pk=donation_receipt_pk)
        if not acquired:
            logging.debug("Could not acquire update lock")
            return
        evm_fund_manager = EVMFundManager(donation_receipt.chain)
        try:
            if evm_fund_manager.is_tx_verified(donation_receipt.tx_hash) is False:
                donation_receipt.delete()
                return
            user = donation_receipt.user_profile
            tx = evm_fund_manager.get_tx(donation_receipt.tx_hash)
            if tx.get('from').lower() not in user.wallets.annotate(
                    lower_address=Func(F('address'), function='LOWER')).values_list('lower_address', flat=True):
                donation_receipt.delete()
                return
            if evm_fund_manager.to_checksum_address(
                    tx.get('to')) != evm_fund_manager.get_fund_manager_checksum_address():
                donation_receipt.delete()
                return
            donation_receipt.value = str(evm_fund_manager.from_wei(tx.get('value')))
            if donation_receipt.chain.is_testnet is False:
                try:
                    token_price = TokenPrice.objects.get(symbol=donation_receipt.chain.symbol)
                    donation_receipt.total_price = str(
                        decimal.Decimal(donation_receipt.value) * decimal.Decimal(token_price.usd_price))
                except TokenPrice.DoesNotExist:
                    logging.error(f'TokenPrice for Chain: {donation_receipt.chain.chain_name} did not defined')
                    donation_receipt.status = ClaimReceipt.PROCESSED_FOR_TOKENTAP_REJECT
                    donation_receipt.save()
                    return
            else:
                donation_receipt.total_price = str(0)
            donation_receipt.status = ClaimReceipt.VERIFIED
            donation_receipt.save()
        except (web3.exceptions.TransactionNotFound, web3.exceptions.TimeExhausted):
            donation_receipt.delete()
            return


@shared_task
def update_donation_receipt_pending_status():
    """
    update status of pending donation receipt
    """
    pending_donation_receipts = DonationReceipt.objects.filter(status=ClaimReceipt.PROCESSED_FOR_TOKENTAP)
    for pending_donation_receipt in pending_donation_receipts:
        process_donation_receipt.delay(pending_donation_receipt.pk)
