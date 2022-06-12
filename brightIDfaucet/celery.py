import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brightIDfaucet.settings')

app = Celery('unitap')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    # Executes at sunset in Melbourne
    'process-pending-tx': {
        'task': 'faucet.tasks.process_pending_receipts_with_no_hash',
        'schedule': 3,
    },
    'update-pending-tx': {
        'task': 'faucet.tasks.update_pending_receipts_status',
        'schedule': 3,
    },
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
