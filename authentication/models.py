import uuid
from django.db import models
from faucet.models import Chain
from django.contrib.auth.models import User
from authentication.helpers import BRIGHTID_SOULDBOUND_INTERFACE


class ProfileManager(models.Manager):
    def get_or_create(self, first_context_id):
        try:
            return super().get_queryset().get(initial_context_id=first_context_id)
        except Profile.DoesNotExist:
            _user = User.objects.create_user(username=first_context_id)
            _profile = Profile(user=_user, initial_context_id=first_context_id)
            _profile.is_aura_verified
            _profile.is_meet_verified
            _profile.save()
            return _profile


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    initial_context_id = models.CharField(max_length=512, unique=True)

    objects = ProfileManager()

    # TODO ask if these make bad things happen in admin panel
    @property
    def is_meet_verified(self):
        (
            is_verified,
            context_ids,
        ) = BRIGHTID_SOULDBOUND_INTERFACE.get_verification_status(
            self.initial_context_id, "Meet"
        )

        return is_verified

    @property
    def is_aura_verified(self):
        (
            is_verified,
            context_ids,
        ) = BRIGHTID_SOULDBOUND_INTERFACE.get_verification_status(
            self.initial_context_id, "Aura"
        )

        return is_verified


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
