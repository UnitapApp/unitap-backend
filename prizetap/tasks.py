import time

import requests
from celery import shared_task
from django.utils import timezone

from brightIDfaucet.settings import DEPLOYMENT_ENV
from core.helpers import memcache_lock

from .models import Raffle
from .utils import PrizetapContractClient, VRFClientContractClient


@shared_task(bind=True)
def set_raffle_random_words(self):
    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return

        raffle = (
            Raffle.objects.filter(deadline__lt=timezone.now())
            .filter(status=Raffle.Status.VERIFIED)
            .filter(vrf_tx_hash__isnull=False)
            .first()
        )

        if raffle:
            print(f"Setting the raffle {raffle.name} random words")
            vrf_client = VRFClientContractClient(raffle.chain)
            last_request = vrf_client.get_last_request()
            expiration_time = last_request[0]
            now = int(time.time())
            if now < expiration_time:
                set_random_words(raffle)
            else:
                print("Random words have expired")
                raffle.vrf_tx_hash = None
                raffle.save()


def set_random_words(raffle: Raffle):
    app = "unitap" if DEPLOYMENT_ENV == "main" else "stage_unitap"
    muon_response = requests.get(
        (
            f"https://shield.unitap.app/v1/?app={app}&method=random-words&"
            f"params[chainId]={raffle.chain.chain_id}&params[prizetapRaffle]={raffle.contract}&"
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
        print(muon_response["error"]["message"])


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

        raffles_queryset = Raffle.objects.filter(deadline__lt=timezone.now()).filter(status=Raffle.Status.WINNERS_SET)
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                print(f"Getting the winner of raffle {raffle.name}")
                raffle_client = PrizetapContractClient(raffle)
                winner_addresses = raffle_client.get_raffle_winners()
                for addr in winner_addresses:
                    if addr and addr != "0x0000000000000000000000000000000000000000":
                        winner_entry = raffle.entries.filter(user_profile__wallets__address__iexact=addr).get()
                        winner_entry.is_winner = True
                        winner_entry.save()
                        raffle.status = Raffle.Status.CLOSED
                        raffle.save()


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
                if raffle.number_of_onchain_entries > 0:
                    print(f"Request random words for the raffle {raffle.name}")
                    request_random_words(raffle)
                    break


def request_random_words(raffle: Raffle):
    vrf_client = VRFClientContractClient(raffle.chain)
    raffle_client = PrizetapContractClient(raffle)
    winners_count = raffle_client.get_raffle_winners_count()
    tx_hash = vrf_client.request_random_words(winners_count)
    if tx_hash:
        raffle.vrf_tx_hash = tx_hash
        raffle.save()
