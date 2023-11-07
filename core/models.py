import inspect

from django.db import models
from django.utils.translation import gettext_lazy as _

from .constraints import BrightIDAuraVerification, BrightIDMeetVerification


class UserConstraint(models.Model):
    class Meta:
        abstract = True

    class Type(models.TextChoices):
        VERIFICATION = "VER", _("Verification")
        TIME = "TIME", _("Time")

    constraints = [BrightIDMeetVerification, BrightIDAuraVerification]

    name = models.CharField(
        max_length=255,
        unique=True,
        choices=[(f'{inspect.getmodule(c).__name__.split(".")[0]}.{c.__name__}', c.__name__) for c in constraints],
    )
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.VERIFICATION)
    description = models.TextField(null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    icon_url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def create_name_field(cls, constraints):
        return models.CharField(
            max_length=255,
            unique=True,
            choices=[(f'{inspect.getmodule(c).__name__.split(".")[0]}.{c.__name__}', c.__name__) for c in constraints],
        )


class TokenPrice(models.Model):
    usd_price = models.CharField(max_length=255, null=False)
    datetime = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    price_url = models.URLField(max_length=255, null=True, blank=True)
    symbol = models.CharField(max_length=255, db_index=True, unique=True, null=False, blank=False)


class BigNumField(models.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 200  # or some other number
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return "numeric"

    def get_internal_type(self):
        return "BigNumField"

    def to_python(self, value):
        if isinstance(value, str):
            return int(value)

        return value

    def get_prep_value(self, value):
        return str(value)
