from django.contrib import admin

from .models import (
    BrightUser,
    Chain,
    ClaimReceipt,
    DonationReceipt,
    GlobalSettings,
    LightningConfig,
    TransactionBatch,
    WalletAccount,
)


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


class TXHashFilter(admin.SimpleListFilter):
    title = "has tx hash"  # or use _('country') for translated title
    parameter_name = "has_tx_hash"

    def lookups(self, request, model_admin):
        return (
            ("has tx hash", ("has tx hash")),
            ("no tx hash", ("no tx hash")),
        )

    def queryset(self, request, queryset):
        if self.value() == "has tx hash":
            return queryset.filter(batch__tx_hash__isnull=False)
        if self.value() == "no tx hash":
            return queryset.filter(batch__tx_hash__isnull=True)


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
    list_filter = ["chain", "_status", TXHashFilter]

    def batch__tx_hash(self, obj):
        if obj.batch:
            return obj.batch.tx_hash


class WalletAccountAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "address"]


class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ["pk", "gastap_round_claim_limit", "tokentap_round_claim_limit"]
    list_editable = ["gastap_round_claim_limit", "tokentap_round_claim_limit"]


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
        # "claims_amount",
    ]
    search_fields = ["tx_hash"]
    list_filter = ["chain", "_status", "updating"]


class LightningConfigAdmin(admin.ModelAdmin):
    readonly_fields = ["claimed_amount", "current_round"]
    list_display = ["pk", "period", "period_max_cap", "claimed_amount", "current_round"]


class DonationReceiptAdmin(admin.ModelAdmin):
    list_display = ["tx_hash", "user_profile", "chain", "value", "total_price", "datetime"]
    search_fields = ["tx_hash"]
    list_filter = ["chain", "user_profile"]


admin.site.register(WalletAccount, WalletAccountAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(BrightUser, BrightUserAdmin)
admin.site.register(ClaimReceipt, ClaimReceiptAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)
admin.site.register(TransactionBatch, TransactionBatchAdmin)
admin.site.register(LightningConfig, LightningConfigAdmin)
admin.site.register(DonationReceipt, DonationReceiptAdmin)
