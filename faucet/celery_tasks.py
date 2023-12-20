import decimal
import logging

import requests
import web3.exceptions
from django.db import transaction
from django.db.models import F, Func
from django.utils import timezone
from sentry_sdk import capture_exception

from authentication.models import NetworkTypes, Wallet
from core.models import TokenPrice
from core.utils import Web3Utils
from tokenTap.models import TokenDistributionClaim

from .faucet_manager.fund_manager import FundMangerException, get_fund_manager
from .models import ClaimReceipt, DonationReceipt, Faucet, TransactionBatch


def has_pending_batch(faucet):
    return TransactionBatch.objects.filter(
        faucet=faucet, _status=ClaimReceipt.PENDING
    ).exists()


class CeleryTasks:
    @staticmethod
    def process_batch(batch_pk):
        """
        Process a batch of claims and send the funds to the users
        creates an on-chain transaction
        """

        try:
            logging.info(f"Processing Batch {batch_pk}")

            batch = TransactionBatch.objects.get(pk=batch_pk)
            if not batch.should_be_processed:
                return
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
                        wallet_type=batch.faucet.chain.chain_type,
                    ).address,
                    "amount": int(receipt.amount),
                }
                for receipt in batch.claims.all()
            ]
            #####
            logging.info(data)

            try:
                manager = get_fund_manager(batch.faucet)
                tx_hash = manager.multi_transfer(data)
                batch.tx_hash = tx_hash
                batch.save()
            except FundMangerException.GasPriceTooHigh as e:
                logging.exception(e)
            except FundMangerException.RPCError as e:
                logging.exception(e)
            except Exception as e:
                capture_exception()
                logging.exception(str(e))
        except TransactionBatch.DoesNotExist:
            pass

    @staticmethod
    def update_pending_batch_with_tx_hash(batch_pk):
        # only one ongoing update per batch
        logging.info("Updating Batch")
        try:
            batch = TransactionBatch.objects.get(pk=batch_pk)
        except TransactionBatch.DoesNotExist:
            return
        try:
            if not batch.status_should_be_updated:
                return
            manager = get_fund_manager(batch.faucet)

            if manager.is_tx_verified(batch.tx_hash):
                batch._status = ClaimReceipt.VERIFIED
            elif batch.is_expired:
                batch._status = ClaimReceipt.REJECTED
        except Exception as e:
            if batch.is_expired:
                batch._status = ClaimReceipt.REJECTED
            capture_exception()
            logging.exception(str(e))
        finally:
            batch.save()
            batch.claims.update(_status=batch._status)

    @staticmethod
    def reject_expired_pending_claims():
        ClaimReceipt.objects.filter(
            batch=None,
            _status=ClaimReceipt.PENDING,
            datetime__lte=timezone.now()
            - timezone.timedelta(minutes=ClaimReceipt.MAX_PENDING_DURATION),
        ).update(_status=ClaimReceipt.REJECTED)

    @staticmethod
    def process_faucet_pending_claims(faucet_id):
        with transaction.atomic():
            faucet = Faucet.objects.select_for_update().get(
                pk=faucet_id
            )  # lock based on chain

            # all pending batches must be resolved before new transactions can be made
            if has_pending_batch(faucet):
                return

            # get all pending receipts for this chain
            # pending receipts are receipts that have not been batched yet
            receipts = ClaimReceipt.objects.filter(
                faucet=faucet, _status=ClaimReceipt.PENDING, batch=None
            )

            if receipts.count() == 0:
                return

            if faucet.chain.chain_type == NetworkTypes.LIGHTNING:
                receipts = receipts.order_by("pk")[:1]
            else:
                receipts = receipts.order_by("pk")[:32]

            # if there are no pending batches, create a new batch
            batch = TransactionBatch.objects.create(faucet=faucet)

            # assign the batch to the receipts
            for receipt in receipts:
                receipt.batch = batch
                receipt.save()

    @staticmethod
    def update_needs_funding_status_faucet(faucet_id):
        try:
            faucet = Faucet.objects.get(pk=faucet_id)
            # if has enough funds and enough fees, needs_funding is False

            faucet.needs_funding = True

            if faucet.has_enough_funds and faucet.has_enough_fees:
                faucet.needs_funding = False

            faucet.save()
        except Exception as e:
            logging.exception(str(e))
            capture_exception()

    @staticmethod
    def process_verified_lightning_claim(gas_tap_claim_id):
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
                logging.info("No tokentap claim found for user")
                return

            tokentap_lightning_claim.status = ClaimReceipt.VERIFIED
            tokentap_lightning_claim.tx_hash = claim.tx_hash
            tokentap_lightning_claim.save()

            claim._status = ClaimReceipt.PROCESSED_FOR_TOKENTAP
            claim.save()

        except Exception as e:
            capture_exception()
            logging.exception(f"error in processing lightning claims: {str(e)}")

    @staticmethod
    def process_rejected_lightning_claim(gas_tap_claim_id):
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
                logging.info("No tokentap claim found for user")
                return

            tokentap_lightning_claim.delete()

            claim._status = ClaimReceipt.PROCESSED_FOR_TOKENTAP_REJECT
            claim.save()

        except Exception as e:
            capture_exception()
            logging.exception(f"error in processing lightning claims: {str(e)}")

    @staticmethod
    def update_token_price(token_pk):
        with transaction.atomic():
            try:
                token = TokenPrice.objects.select_for_update().get(pk=token_pk)
            except TokenPrice.DoesNotExist:
                logging.error(f"TokenPrice with pk {token_pk} does not exist.")
                return

            def parse_request(token: TokenPrice, request_res: requests.Response):
                try:
                    request_res.raise_for_status()
                    json_data = request_res.json()
                    token.usd_price = str(json_data.json()[0].get("current_price"))
                    token.save()
                except requests.HTTPError as e:
                    logging.exception(
                        f"requests for url: {request_res.url} can not fetched"
                        f" with status_code: {request_res.status_code}. "
                        f"{str(e)}"
                    )

                except KeyError as e:
                    logging.exception(
                        f"requests for url: {request_res.url} data do not have"
                        f" property keys for loading data. {str(e)}"
                    )

                except Exception as e:
                    logging.exception(
                        f"requests for url: {request_res.url} got error "
                        f"{type(e).__name__}. {str(e)}"
                    )

            parse_request(token, requests.get(token.price_url, timeout=5))

    @staticmethod
    def process_donation_receipt(donation_receipt_pk):
        donation_receipt = DonationReceipt.objects.get(pk=donation_receipt_pk)
        evm_fund_manager = get_fund_manager(donation_receipt.faucet)
        try:
            if not evm_fund_manager.is_tx_verified(donation_receipt.tx_hash):
                donation_receipt.delete()
                return
            user = donation_receipt.user_profile
            tx = evm_fund_manager.get_tx(donation_receipt.tx_hash)
            if tx.get("from").lower() not in user.wallets.annotate(
                lower_address=Func(F("address"), function="LOWER")
            ).values_list("lower_address", flat=True):
                donation_receipt.delete()
                return
            if (
                Web3Utils.to_checksum_address(tx.get("to"))
                != evm_fund_manager.get_fund_manager_checksum_address()
            ):
                donation_receipt.delete()
                return
            donation_receipt.value = str(evm_fund_manager.from_wei(tx.get("value")))
            if not donation_receipt.faucet.chain.is_testnet:
                try:
                    token_price = TokenPrice.objects.get(
                        symbol=donation_receipt.faucet.chain.symbol
                    )
                    donation_receipt.total_price = str(
                        decimal.Decimal(donation_receipt.value)
                        * decimal.Decimal(token_price.usd_price)
                    )
                except TokenPrice.DoesNotExist:
                    logging.error(
                        f"TokenPrice for Chain: "
                        f"{donation_receipt.faucet.chain.chain_name}"
                        f" did not defined"
                    )
                    donation_receipt.status = ClaimReceipt.REJECTED
                    donation_receipt.save()
                    return
            else:
                donation_receipt.total_price = str(0)
            donation_receipt.status = ClaimReceipt.VERIFIED
            donation_receipt.save()
        except (web3.exceptions.TransactionNotFound, web3.exceptions.TimeExhausted):
            donation_receipt.delete()
            return
