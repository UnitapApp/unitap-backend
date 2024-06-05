from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from authentication.models import UserProfile


class Season(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        INACTIVE = "INACTIVE", _("Inactive")

    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    sponsor = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )

    def save(self, *args, **kwargs):
        if self.status == self.Status.ACTIVE:
            assert not Season.objects.filter(
                ~Q(pk=self.pk), status=self.Status.ACTIVE
            ).exists(), "There is already an active season"

        super().save(*args, **kwargs)


class SeasonLevel(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="levels")
    required_xp = models.PositiveIntegerField()


class XPRecord(models.Model):
    context = models.CharField(max_length=255)
    xp = models.PositiveBigIntegerField()
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="xp_records"
    )
    user = models.ForeignKey(
        UserProfile, on_delete=models.DO_NOTHING, related_name="xp_records"
    )
    created_at = models.DateTimeField(auto_now_add=True)
