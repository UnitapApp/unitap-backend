import csv
import logging
import time

import requests
from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from web3 import Web3

from authentication.models import NetworkTypes, UserProfile, Wallet
from brightIDfaucet.settings import DEPLOYMENT_ENV
from core.helpers import memcache_lock
from core.thirdpartyapp import Subgraph

from .models import Raffle, RaffleEntry
from .utils import PrizetapContractClient, VRFClientContractClient


@shared_task(bind=True)
def set_raffle_random_words(self):
    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return

        raffles_queryset = (
            Raffle.objects.filter(deadline__lt=timezone.now())
            .filter(status=Raffle.Status.VERIFIED)
            .filter(vrf_tx_hash__isnull=False)
            .exclude(vrf_tx_hash__exact="")
        )

        if raffles_queryset.count() > 0:
            vrf_client = VRFClientContractClient()
            last_request = vrf_client.get_last_request()
            expiration_time = last_request[0]
            num_words = last_request[1]
            now = int(time.time())
            if now >= expiration_time:
                print("Random words have expired")
                raffles_queryset.update(vrf_tx_hash=None)
                return
            for raffle in raffles_queryset:
                try:
                    if num_words == raffle.winners_count:
                        print(f"Setting the raffle {raffle.name} random words")
                        set_random_words(raffle)
                        break
                    else:
                        raise Exception(f"Mismatch the raffle {raffle.name} num words")
                except Exception as e:
                    raffle.vrf_tx_hash = None
                    raffle.save()
                    logging.error(e)


def set_random_words(raffle: Raffle):
    app = "unitap" if DEPLOYMENT_ENV == "main" else "stage_unitap"
    muon_response = requests.get(
        (
            f"https://shield.unitap.app/v1/?app={app}&method=random-words&"
            f"params[chainId]={raffle.chain.chain_id}"
            f"&params[prizetapRaffle]={raffle.contract}&"
            f"params[raffleId]={raffle.raffleId}"
        )
    )
    muon_response = muon_response.json()
    if muon_response["success"]:
        muon_response = muon_response["result"]
        muon_data = muon_response["data"]["result"]
        raffle_client = PrizetapContractClient(raffle)
        random_words = [int(r) for r in muon_data["randomWords"]]
        raffle_client.set_raffle_random_words(
            int(muon_data["expirationTime"]),
            random_words,
            muon_response["reqId"],
            (
                int(muon_response["signatures"][0]["signature"], 16),
                muon_response["signatures"][0]["owner"],
                muon_response["data"]["init"]["nonceAddress"],
            ),
            muon_response["shieldSignature"],
        )
        raffle.status = Raffle.Status.RANDOM_WORDS_SET
        raffle.save()
    else:
        print(
            muon_response["error"]["message"],
            (
                f"Error {muon_response['error']['detail']} has been "
                f"raised in the raffle {raffle.raffleId}"
            ),
        )


@shared_task(bind=True)
def set_raffle_winners(self):
    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return

        raffles_queryset = Raffle.objects.filter(deadline__lt=timezone.now()).filter(
            status=Raffle.Status.RANDOM_WORDS_SET
        )
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                print(f"Setting the raffle {raffle.name} winners")
                raffle_client = PrizetapContractClient(raffle)
                tx_hash = raffle_client.set_winners()
                if tx_hash:
                    raffle.status = Raffle.Status.WINNERS_SET
                    raffle.save()


@shared_task(bind=True)
def get_raffle_winners(self):
    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return

        raffles_queryset = Raffle.objects.filter(deadline__lt=timezone.now()).filter(
            status=Raffle.Status.WINNERS_SET
        )
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                try:
                    print(f"Getting the winner of raffle {raffle.name}")
                    raffle_client = PrizetapContractClient(raffle)
                    winner_addresses = raffle_client.get_raffle_winners()
                    for addr in winner_addresses:
                        if (
                            addr
                            and addr != "0x0000000000000000000000000000000000000000"
                        ):
                            winner_entry = raffle.entries.filter(
                                user_profile__wallets__address__iexact=addr
                            ).get()
                            winner_entry.is_winner = True
                            winner_entry.save()
                            raffle.status = Raffle.Status.CLOSED
                            raffle.save()
                except Exception as e:
                    logging.error(e)


@shared_task(bind=True)
def request_random_words_for_expired_raffles(self):
    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return

        raffles_queryset = (
            Raffle.objects.filter(deadline__lt=timezone.now())
            .filter(status=Raffle.Status.VERIFIED)
            .filter(vrf_tx_hash__isnull=True)
        )
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                try:
                    if raffle.number_of_onchain_entries > 0:
                        print(f"Request random words for the raffle {raffle.name}")
                        request_random_words(raffle)
                        break
                except Exception as e:
                    logging.error(e)


def request_random_words(raffle: Raffle):
    vrf_client = VRFClientContractClient()
    raffle_client = PrizetapContractClient(raffle)
    winners_count = raffle_client.get_raffle_winners_count()
    tx_hash = vrf_client.request_random_words(winners_count)
    if tx_hash:
        raffle.vrf_tx_hash = tx_hash
        raffle.save()


@shared_task(bind=True)
def set_raffle_ids(self):
    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return
        raffles_queryset = (
            Raffle.objects.filter(status=Raffle.Status.PENDING)
            .filter(raffleId__isnull=True)
            .filter(tx_hash__isnull=False)
            .order_by("id")
        )
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                try:
                    print(f"Setting the raffle {raffle.name} raffleId")
                    contract_client = PrizetapContractClient(raffle)

                    receipt = contract_client.web3_utils.get_transaction_receipt(
                        raffle.tx_hash
                    )
                    log = contract_client.get_raffle_created_log(receipt)

                    raffle.raffleId = log["args"]["raffleId"]
                    raffle.status = Raffle.Status.VERIFIED
                    onchain_raffle = contract_client.get_raffle()
                    is_valid = True
                    if onchain_raffle["status"] != 0:
                        is_valid = False
                        logging.error(f"Mismatch raffle {raffle.pk} status")
                    if onchain_raffle["lastParticipantIndex"] != 0:
                        is_valid = False
                        logging.error(
                            f"Mismatch raffle {raffle.pk} lastParticipantIndex"
                        )
                    if onchain_raffle["lastWinnerIndex"] != 0:
                        is_valid = False
                        logging.error(f"Mismatch raffle {raffle.pk} lastWinnerIndex")
                    if onchain_raffle["participantsCount"] != 0:
                        is_valid = False
                        logging.error(f"Mismatch raffle {raffle.pk} participantsCount")
                    if raffle.creator_address != onchain_raffle["initiator"]:
                        is_valid = False
                        logging.error(f"Mismatch raffle {raffle.pk} initiator")
                    if (
                        raffle.max_number_of_entries
                        != onchain_raffle["maxParticipants"]
                    ):
                        is_valid = False
                        logging.error(f"Mismatch raffle {raffle.pk} maxParticipants")
                    if raffle.max_multiplier != onchain_raffle["maxMultiplier"]:
                        is_valid = False
                        logging.error(f"Mismatch raffle {raffle.pk} maxMultiplier")
                    if int(raffle.start_at.timestamp()) != onchain_raffle["startTime"]:
                        is_valid = False
                        logging.error(f"Mismatch raffle {raffle.pk} startTime")
                    if int(raffle.deadline.timestamp()) != onchain_raffle["endTime"]:
                        is_valid = False
                        logging.error(f"Mismatch raffle {raffle.pk} endTime")
                    if raffle.winners_count != onchain_raffle["winnersCount"]:
                        is_valid = False
                        logging.error(f"Mismatch raffle {raffle.pk} winnersCount")
                    if raffle.is_prize_nft:
                        if raffle.prize_asset != onchain_raffle["collection"]:
                            is_valid = False
                            logging.error(f"Mismatch raffle {raffle.pk} collection")
                    else:
                        if raffle.prize_amount != onchain_raffle["prizeAmount"]:
                            is_valid = False
                            logging.error(f"Mismatch raffle {raffle.pk} prizeAmount")
                        if raffle.prize_asset != onchain_raffle["currency"]:
                            is_valid = False
                            logging.error(f"Mismatch raffle {raffle.pk} currency")
                    if not is_valid:
                        raffle.raffleId = None
                        raffle.status = Raffle.Status.REJECTED

                    raffle.save()
                except Exception as e:
                    logging.error(e)


@shared_task
def update_prizetap_winning_chance_number():
    sub = Subgraph()
    holders = sub.get_unitap_pass_holders()
    for holder_address, unitap_pass_ids in holders.items():
        try:
            user_profile = (
                Wallet.objects.prefetch_related()
                .get(address__iexact=holder_address, wallet_type=NetworkTypes.EVM)
                .user_profile
            )
            with transaction.atomic():
                user_profile.prizetap_winning_chance_number = F(
                    "prizetap_winning_chance_number"
                ) + len(unitap_pass_ids)
                user_profile.save(update_fields=("prizetap_winning_chance_number",))
        except Wallet.DoesNotExist:
            logging.warning(f"Wallet address: {holder_address} not exists.")


@shared_task(bind=True)
def process_raffles_pre_enrollments(self):
    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return

        with transaction.atomic():
            queryset = (
                Raffle.objects.exclude(pre_enrollment_file__isnull=True)
                .exclude(pre_enrollment_file__exact="")
                .filter(status=Raffle.Status.VERIFIED)
                .filter(is_processed=False)
                .order_by("id")
            )
            for raffle in queryset:
                print(f"Process the raffle {raffle.pk} pre-enrollments")
                file_path = raffle.pre_enrollment_file.path
                print(file_path)
                with open(file_path, newline="") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        user_profile = UserProfile.objects.get_by_wallet_address(
                            Web3.to_checksum_address(row[0])
                        )
                        entry = RaffleEntry(
                            raffle=raffle,
                            user_profile=user_profile,
                            user_wallet_address=row[0],
                            multiplier=row[1],
                            pre_enrollment=True,
                        )
                        entry.save()
                raffle.is_processed = True
                raffle.save()


@shared_task(bind=True)
def onchain_pre_enrollments(self):
    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return
        entries_queryset = (
            RaffleEntry.objects.filter(pre_enrollment=True)
            .filter(tx_hash__isnull=True)
            .order_by("id")
        )
        batch_size = 50
        if entries_queryset.count() > 0:
            first_entry = entries_queryset.first()

            batch_entry = entries_queryset.filter(raffle=first_entry.raffle).all()[
                :batch_size
            ]

            entry_pack = []
            weight_pack = []

            for entry in batch_entry:
                entry_pack.append(entry.user_wallet_address)
                weight_pack.append(entry.multiplier)

            try:
                contract_client = PrizetapContractClient(first_entry.raffle)
                tx_hash = contract_client.batch_participate(entry_pack, weight_pack)

                with transaction.atomic():
                    for entry in batch_entry:
                        entry.tx_hash = tx_hash
                        entry.save()
            except Exception as e:
                logging.error(
                    f"Unable to pre-enroll raffle {first_entry.raffle.pk} entries"
                )
                logging.error(e)
