from django.db import models

# Create your models here.


class Permission(models.Model):
    name = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(Permission, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def is_valid(self, *args, **kwargs):
        # Override this method in subclasses
        return False


class BrightIDMeetVerification(Permission):
    def is_valid(self, user_profile, *args, **kwargs):
        return user_profile.is_meet_verified


class BrightIDAuraVerification(Permission):
    def is_valid(self, user_profile, *args, **kwargs):
        return user_profile.is_aura_verified
