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
        )
        if raffles_queryset.count() > 0:
            for raffle in raffles_queryset:
                if raffle.number_of_onchain_entries > 0 and not raffle.winner_entry:
                    print(f"Drawing the raffle {raffle.name}")
                    raffle_client = PrizetapContractClient(raffle)
                    if raffle_client.draw_raffle():
                        raffle.is_active = False
                        raffle.save()
