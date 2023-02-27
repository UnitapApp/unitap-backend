import uuid
from django.db import models
from faucet.models import Chain
from django.contrib.auth.models import User


class ProfileManager(models.Manager):
    def get_or_create(self, first_context_id):
        try:
            return super().get_queryset().get(initial_context_id=first_context_id)
        except Profile.DoesNotExist:
            _user = User.objects.create_user(username=first_context_id)
            _profile = Profile(user=_user, initial_context_id=first_context_id)
            # get verifications from brightId
            _profile.save()
            return _profile


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    initial_context_id = models.UUIDField(default=uuid.uuid4, unique=True)

    @property
    def is_meet_verified(self):
        return True

    @property
    def is_aura_verified(self):
        return True


class EVMWallet(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    address = models.CharField(max_length=45, unique=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.profile.initial_context_id} - {self.address}"


class SolanaWallet(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    address = models.CharField(max_length=45, unique=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.profile.initial_context_id} - {self.address}"


class BitcoinLightningWallet(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    address = models.CharField(max_length=45, unique=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.profile.initial_context_id} - {self.address}"
