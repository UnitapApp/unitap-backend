from django.contrib import admin
from .models import *


class ChainAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "chain_name",
        "chain_id",
        "symbol",
        "chain_type",
        "needs_funding",
        "order",
    ]
    list_editable = ["order"]


class BrightUserAdmin(admin.ModelAdmin):
    list_display = ["pk", "address", "context_id"]
    search_fields = ["address", "context_id"]


def last_updated_with_seconds(obj):
    return obj.last_updated.strftime("%B %d, %Y, %I:%M:%S %p")


last_updated_with_seconds.short_description = "Last Updated"


class ClaimReceiptAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "batch__tx_hash",
        "chain",
        "user_profile",
        "_status",
        "age",
        last_updated_with_seconds,
    ]
    list_filter = ["chain", "_status"]

    def batch__tx_hash(self, obj):
        if obj.batch:
            return obj.batch.tx_hash


class WalletAccountAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "address"]


class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ["pk", "weekly_chain_claim_limit", "tokentap_weekly_claim_limit"]
    list_editable = ["weekly_chain_claim_limit", "tokentap_weekly_claim_limit"]


class TransactionBatchAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "_status",
        "tx_hash",
        "updating",
        "chain",
        "age",
        "is_expired",
        "claims_count",
        "claims_amount",
    ]
    search_fields = ["tx_hash"]
    list_filter = ["chain", "_status", "updating"]


class LightningConfigAdmin(admin.ModelAdmin):
    readonly_fields = ["claimed_amount", "current_round"]
    list_display = ["pk", "period", "period_max_cap", "claimed_amount", "current_round"]
    pass


admin.site.register(WalletAccount, WalletAccountAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(BrightUser, BrightUserAdmin)
admin.site.register(ClaimReceipt, ClaimReceiptAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)
admin.site.register(TransactionBatch, TransactionBatchAdmin)
admin.site.register(LightningConfig, LightningConfigAdmin)
