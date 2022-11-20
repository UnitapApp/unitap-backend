from django.contrib import admin
from .models import *


class ChainAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "chain_name",
        "chain_id",
        "symbol",
        "order",
        "total_claims",
        "total_claims_since_last_monday",
    ]
    list_editable = ["order"]


class BrightUserAdmin(admin.ModelAdmin):
    list_display = ["pk", "address", "context_id"]


class ClaimReceiptAdmin(admin.ModelAdmin):
    list_display = ["pk", "batch__tx_hash", "chain", "bright_user", "_status", "age"]

    def batch__tx_hash(self, obj):
        if obj.batch:
            return obj.batch.tx_hash


class WalletAccountAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "address"]


class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ["pk", "weekly_chain_claim_limit"]
    list_editable = [
        "weekly_chain_claim_limit",
    ]


class TransactionBatchAdmin(admin.ModelAdmin):
    list_display = ["pk", "_status", "tx_hash", "updating"]


admin.site.register(WalletAccount, WalletAccountAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(BrightUser, BrightUserAdmin)
admin.site.register(ClaimReceipt, ClaimReceiptAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)
admin.site.register(TransactionBatch, TransactionBatchAdmin)
