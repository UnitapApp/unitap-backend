import os

from celery import Celery

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
    "update_tokentap_claim_for_verified_lightning_claims": {
        "task": "faucet.tasks.update_tokentap_claim_for_verified_lightning_claims",
        "schedule": 9,
    },
    "update-tokens-price": {
        "task": "faucet.tasks.update_tokens_price",
        "schedule": 600,
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
    "register-competition-to-start": {
        "task": "quiztap.tasks.register_competition_to_start",
        "schedule": 10,
    },
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
