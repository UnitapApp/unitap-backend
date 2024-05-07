from django.contrib import admin

from core.admin import UserConstraintBaseAdmin

from .models import (
    Constraint,
    GlobalSettings,
    TokenDistribution,
    TokenDistributionClaim,
)

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


class TokenDistributionClaimAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "token_distribution",
        "status",
        "user_profile",
        "age",
        "user_wallet_address",
    ]
    search_fields = ["user_wallet_address"]
    list_filter = ["token_distribution", "status"]


class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ["pk", "index", "value"]
    list_editable = ["value"]


admin.site.register(Constraint, UserConstraintBaseAdmin)
admin.site.register(TokenDistribution, TokenDistributionAdmin)
admin.site.register(TokenDistributionClaim, TokenDistributionClaimAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)
