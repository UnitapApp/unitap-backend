from celery import shared_task
from django.utils import timezone
from core.helpers import memcache_lock
from .models import Raffle
from .utils import PrizetapContractClient


@shared_task(bind=True)
def draw_the_expired_raffles(self):

    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return

        raffles_queryset = (
            Raffle.objects
            .filter(deadline__lt=timezone.now())
            .filter(status=Raffle.Status.PENDING)
        )
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                if raffle.number_of_onchain_entries > 0 and not raffle.winner_entry:
                    print(f"Drawing the raffle {raffle.name}")
                    raffle_client = PrizetapContractClient(raffle)
                    tx_hash = raffle_client.draw_raffle()
                    receipt = raffle_client.wait_for_transaction_receipt(
                        tx_hash)
                    if receipt['status'] == 1:
                        raffle.status = Raffle.Status.HELD
                        raffle.save()


@shared_task(bind=True)
def set_the_winner_of_raffles(self):

    id = f"{self.name}-LOCK"

    with memcache_lock(id, self.app.oid) as acquired:
        if not acquired:
            print(f"Could not acquire process lock at {self.name}")
            return

        raffles_queryset = (
            Raffle.objects
            .filter(deadline__lt=timezone.now())
            .filter(status=Raffle.Status.HELD)
        )
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                print(f"Setting the winner of raffle {raffle.name}")
                raffle_client = PrizetapContractClient(raffle)
                winner_address = raffle_client.get_raffle_winner()
                if winner_address and winner_address != "0x0000000000000000000000000000000000000000":
                    try:
                        winner_entry = raffle.entries.filter(
                            user_profile__wallets__address__iexact=winner_address).get()
                        winner_entry.is_winner = True
                        winner_entry.save()
                        raffle.status = Raffle.Status.WINNER_SET
                        raffle.save()
                    except Exception as e:
                        print(e)
                        pass
