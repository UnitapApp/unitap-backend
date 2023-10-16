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
        "schedule": 3,
    },
    'update-tokens-price': {
        "task": "faucet.tasks.update_tokens_price",
        "schedule": 600,
    },
    'update-donation-receipt-status': {
        "task": "faucet.tasks.update_donation_receipt_pending_status",
        "schedule": 180,
    },
    "draw-prizetap-raffles": {
        "task": "prizetap.tasks.draw_the_expired_raffles",
        "schedule": 300
    },
    "set-raffle-winner": {
        "task": "prizetap.tasks.set_the_winner_of_raffles",
        "schedule": 300
    },
    "request-random-words-for-linea-raffles": {
        "task": "prizetap.tasks.request_random_words_for_expired_linea_raffles",
        "schedule": 300
    },
    "draw-linea-raffles": {
        "task": "prizetap.tasks.draw_expired_linea_raffles",
        "schedule": 300
    },
    "set-linea-raffle-winners": {
        "task": "prizetap.tasks.set_the_winner_of_linea_raffles",
        "schedule": 300
    }
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
