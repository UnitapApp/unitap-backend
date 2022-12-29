from django.core.management.base import BaseCommand, CommandError
from faucet.models import ClaimReceipt, BrightUser, Chain, TransactionBatch
import json
import os
from datetime import datetime
from django.utils.timezone import make_aware

from django.conf import settings


class Command(BaseCommand):
    help = "Fixes deleted Optimism records"

    def handle(self, *args, **options):

        # print debug status
        self.stdout.write(self.style.SUCCESS(f"DEBUG {settings.DEBUG}"))

        # open op_batch.json file
        # read in the json
        # each record in the json is TransactionBatch with chain_id = 10
        # in each batch there is a list of ClaimReceipts
        # for each ClaimReceipt, find the BrightUser and Chain
        # create a new TransactionBatch with the same tx_hash
        # assign the new TransactionBatch to the ClaimReceipts
        # save the ClaimReceipts
        # save the TransactionBatch

        # op_batch.json file path
        file_path = os.path.join(os.path.dirname(__file__), "op_batch.json")

        with open(file_path, "r") as f:
            op_batch = json.load(f)

        # sort the batches by timestamp
        op_batch.sort(key=lambda x: x["timestamp"])

        for batch in op_batch:
            tx_hash = batch["tx_hash"]
            receipts = batch["recipients"]
            timestamp = batch["timestamp"]
            create_datetime = make_aware(datetime.fromtimestamp(int(timestamp)))

            chain = Chain.objects.get(chain_id=10)

            # get the transaction batch if it exists
            try:
                new_batch = TransactionBatch.objects.filter(
                    tx_hash=tx_hash, chain=chain, _status=ClaimReceipt.VERIFIED
                ).first()

                if not new_batch:
                    raise TransactionBatch.DoesNotExist

            except TransactionBatch.DoesNotExist:
                # create a new transaction batch
                new_batch = TransactionBatch.objects.create(
                    chain=chain,
                    tx_hash=tx_hash,
                    _status=ClaimReceipt.VERIFIED,
                    datetime=create_datetime,
                )
                new_batch.save()
                new_batch.datetime = create_datetime
                new_batch.save()
            for receipt in receipts:
                address = receipt[0]
                amount = receipt[1]

                try:
                    user = BrightUser.objects.get(address=address)
                except BrightUser.DoesNotExist:
                    # if it's DEBUG mode, create a new user
                    if settings.DEBUG:
                        user = BrightUser.objects.get_or_create(address=address)
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"User with address {address} does not exist - ({tx_hash})"
                            )
                        )
                        continue

                try:
                    # if this does not fail, the record already exists
                    r = ClaimReceipt.objects.filter(
                        bright_user=user,
                        amount=amount,
                        chain=chain,
                        batch__tx_hash=tx_hash,
                        _status=ClaimReceipt.VERIFIED,
                    ).first()

                    if not r:
                        raise ClaimReceipt.DoesNotExist

                except ClaimReceipt.DoesNotExist:

                    new_receipt = ClaimReceipt.objects.create(
                        chain=chain,
                        bright_user=user,
                        amount=amount,
                        datetime=create_datetime,
                        _status=ClaimReceipt.VERIFIED,
                        batch=new_batch,
                    )
                    new_receipt.save()
                    new_receipt.datetime = create_datetime
                    new_receipt.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"****Successfully created claim receipt {address, amount} - ({tx_hash})"
                        )
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"**Successfully created transaction batch {tx_hash}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Successfully fixed Optimism records"))
