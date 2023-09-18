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
            .filter(is_active=True)
            .filter(status=Raffle.Status.OPEN)
        )
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                if raffle.number_of_onchain_entries > 0 and not raffle.winner_entry:
                    print(f"Drawing the raffle {raffle.name}")
                    raffle_client = PrizetapContractClient(raffle)
                    if raffle_client.draw_raffle():
                        raffle.status = Raffle.Status.HELD
                        raffle.is_active = False
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
            .filter(is_active=False)
            .filter(status=Raffle.Status.HELD)
        )
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                print(f"Setting the winner of raffle {raffle.name}")
                raffle_client = PrizetapContractClient(raffle)
                winner_address = raffle_client.get_raffle_winner()
                if winner_address:
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
