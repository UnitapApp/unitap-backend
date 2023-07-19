from django.db import models
from .constraints import *
from django.utils.translation import gettext_lazy as _

class UserConstraint(models.Model):
    class Meta:
        abstract = True

    class Type(models.TextChoices):
        VERIFICATION = "VER", _("Verification")
        TIME = "TIME", _("Time")

    constraints = [
        BrightIDMeetVerification,
        BrightIDAuraVerification
    ]


    name = models.CharField(max_length=255, unique=True, 
                            choices=[(c.__name__, c.__name__) for c in constraints])
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.VERIFICATION
    )
    response = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name