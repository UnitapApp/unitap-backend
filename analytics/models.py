import uuid

from django.core.cache import cache
from django.db import models

from authentication.models import (
    BrightIDConnection,
    GitcoinPassportConnection,
    UserProfile,
)


class UserAnalytics(models.Model):
    all_users_count = models.IntegerField(default=0)
    brightid_users_count = models.IntegerField(default=0)
    gitcoinpassport_users_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @staticmethod
    def updateData():
        # Check if there's an existing record
        if UserAnalytics.objects.exists():
            # If record exists, update it
            analytics = (
                UserAnalytics.objects.first()
            )  # Assuming there's only one record
            analytics.all_users_count = UserProfile.user_count()
            analytics.brightid_users_count = BrightIDConnection.objects.all().count()
            analytics.gitcoinpassport_users_count = (
                GitcoinPassportConnection.objects.all().count()
            )
            analytics.save()
        else:
            # If no record exists, create a new one
            all_users_count = UserProfile.user_count()
            brightid_users_count = BrightIDConnection.objects.all().count()
            gitcoinpassport_users_count = (
                GitcoinPassportConnection.objects.all().count()
            )
            UserAnalytics.objects.create(
                all_users_count=all_users_count,
                brightid_users_count=brightid_users_count,
                gitcoinpassport_users_count=gitcoinpassport_users_count,
            )
