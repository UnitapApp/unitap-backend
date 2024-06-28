import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "brightIDfaucet.settings")

app = Celery("unitap")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "process-pending-claims": {
        "task": "faucet.tasks.process_pending_claims",
        "schedule": 3,
    },
    "process-pending-batches": {
        "task": "faucet.tasks.process_pending_batches",
        "schedule": 3,
    },
    "update-processed-batches": {
        "task": "faucet.tasks.update_pending_batches_with_tx_hash_status",
        "schedule": 3,
    },
    "update-needs-funding": {
        "task": "faucet.tasks.update_needs_funding_status",
        "schedule": 120,
    },
    "reject-expired-pending-claims": {
        "task": "faucet.tasks.reject_expired_pending_claims",
        "schedule": 120,
    },
    "update-tokens-price": {
        "task": "faucet.tasks.update_tokens_price",
        "schedule": crontab(minute="0", hour="*/2"),
    },
    "update-donation-receipt-status": {
        "task": "faucet.tasks.update_donation_receipt_pending_status",
        "schedule": 180,
    },
    "request-random-words-for-raffles": {
        "task": "prizetap.tasks.request_random_words_for_expired_raffles",
        "schedule": 120,
    },
    "set-raffle-random-words": {
        "task": "prizetap.tasks.set_raffle_random_words",
        "schedule": 120,
    },
    "set-raffle-winners": {
        "task": "prizetap.tasks.set_raffle_winners",
        "schedule": 300,
    },
    "get-raffle-winners": {
        "task": "prizetap.tasks.get_raffle_winners",
        "schedule": 300,
    },
    "set-raffle-ids": {"task": "prizetap.tasks.set_raffle_ids", "schedule": 300},
    "set-token-distribution-ids": {
        "task": "tokenTap.tasks.set_distribution_id",
        "schedule": 300,
    },
    "extend-distribution": {
        "task": "tokenTap.tasks.extend_distribution",
        "schedule": 600,
    },
    "register-competition-to-start": {
        "task": "quiztap.tasks.register_competition_to_start",
        "schedule": 10,
    },
    "update_claims_count_every_10_minutes": {
        "task": "faucet.tasks.update_all_faucets_claims",
        "schedule": 600,
        "args": (False,),
    },
    "update_total_claims_this_round_every_10_minutes": {
        "task": "faucet.tasks.update_all_faucets_claims",
        "schedule": 600,
    },
    "update_prizetap_winning_chance_number_every_week": {
        "task": "prizetap.tasks.update_prizetap_winning_chance_number",
        "schedule": crontab(minute="0", hour="0", day_of_week="1"),
    },
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
