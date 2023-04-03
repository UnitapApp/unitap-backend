from django.db import models
from django.contrib.auth.models import User
from authentication.helpers import BRIGHTID_SOULDBOUND_INTERFACE
from django.utils import timezone


class ProfileManager(models.Manager):
    def get_or_create(self, first_context_id):
        try:
            return super().get_queryset().get(initial_context_id=first_context_id)
        except UserProfile.DoesNotExist:
            _user = User.objects.create_user(username=first_context_id)
            _profile = UserProfile(user=_user, initial_context_id=first_context_id)
            _profile.is_aura_verified
            _profile.is_meet_verified
            _profile.save()
            return _profile


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="profile")
    initial_context_id = models.CharField(max_length=512, unique=True)
    # set a time of creation with default to now
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    objects = ProfileManager()

    @property
    def age(self):
        if self.created_at is None:
            return -1
        return timezone.now() - self.created_at

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


class NetworkTypes:
    EVM = "EVM"
    SOLANA = "Solana"
    LIGHTNING = "Lightning"
    NONEVM = "Non-EVM"

    networks = (
        (EVM, "EVM"),
        (SOLANA, "Solana"),
        (LIGHTNING, "Lightning"),
        (NONEVM, "NONEVM"),
    )


class Wallet(models.Model):
    wallet_type = models.CharField(choices=NetworkTypes.networks, max_length=10)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.PROTECT, related_name="wallets"
    )
    address = models.CharField(max_length=512, unique=True)

    class Meta:
        unique_together = (("wallet_type", "user_profile"),)

    def __str__(self):
        return f"{self.wallet_type} Wallet for profile with contextId {self.user_profile.initial_context_id}"
