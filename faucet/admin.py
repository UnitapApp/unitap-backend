from django.contrib import admin
from .models import *


class ChainAdmin(admin.ModelAdmin):
    list_display = ["pk", "chain_name", "chain_id", "symbol", "order"]
    list_editable = ["order"]


class BrightUserAdmin(admin.ModelAdmin):
    list_display = ["pk", "address", "context_id"]


class ClaimReceiptAdmin(admin.ModelAdmin):
    list_display = ["pk", "tx_hash", "chain", "bright_user", "_status"]


class WalletAccountAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "address"]


class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ["pk", "weekly_chain_claim_limit"]
    list_editable = [
        "weekly_chain_claim_limit",
    ]


admin.site.register(WalletAccount, WalletAccountAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(BrightUser, BrightUserAdmin)
admin.site.register(ClaimReceipt, ClaimReceiptAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)
