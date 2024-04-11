import logging
import time

import requests
from celery import shared_task
from django.utils import timezone

from .models import UserAnalytics

@shared_task(bind=True)
def update_user_analytics(self):
    try:
        UserAnalytics.updateData()
    except Exception as e:
        logging.error(f"Error updating user analytics: {e}")
        raise self.retry(exc=e, countdown=10, max_retries=5)
    

