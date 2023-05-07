from django.contrib import admin
from .models import *

# Register your models here.


class TokenDistributionAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "name",
        "token",
        "token_address",
        "amount",
        "chain",
        "created_at",
        "deadline",
    ]


admin.site.register(TokenDistribution, TokenDistributionAdmin)
