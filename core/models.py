from django.db import models
from .constraints import *

class UserConstraint(models.Model):
    class Meta:
        abstract = True

    constraints = [
        BrightIDMeetVerification,
        BrightIDAuraVerification
    ]


    name = models.CharField(max_length=255, unique=True, 
                            choices=[(c.__name__, c.__name__) for c in constraints])
    response = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name