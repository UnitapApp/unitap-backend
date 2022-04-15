from django.contrib.auth.models import User
from django.db import models
import uuid

from brightIDfaucet.settings import BRIGHT_ID_DRIVER


class BrightUser(models.Model):
    PENDING = "0"
    VERIFIED = "1"

    states = ((PENDING, "Pending"),
              (VERIFIED, "Verified"))

    user = models.OneToOneField(User, related_name="bright_user", on_delete=models.CASCADE)
    context_id = models.UUIDField(default=uuid.uuid4, unique=True)

    _verification_status = models.CharField(max_length=1, choices=states, default=PENDING)

    def get_verification_status(self, bright_driver=BRIGHT_ID_DRIVER) -> states:
        if self._verification_status == self.VERIFIED:
            return self.VERIFIED

        is_verified = bright_driver.get_verification_status(str(self.context_id))

        if is_verified:
            self._verification_status = self.VERIFIED
            self.save()

        return self._verification_status

    def get_verification_url(self, bright_driver=BRIGHT_ID_DRIVER) -> str:
        return bright_driver.get_verification_link(str(self.context_id))
