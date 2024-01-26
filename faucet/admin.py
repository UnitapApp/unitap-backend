from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter, highlight_deleted

from .models import (
    BrightUser,
    ClaimReceipt,
    DonationContract,
    DonationReceipt,
    Faucet,
    GlobalSettings,
    LightningConfig,
    TransactionBatch,
)


class FaucetAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "chain_name",
        "chain_id",
        "symbol",
        "chain_type",
        "needs_funding",
        "is_active",
        "is_one_time_claim",
    ]

    @admin.display(ordering="chain__chain_name")
    def chain_name(self, obj):
        return obj.chain.chain_name

    @admin.display(ordering="chain__chain_id")
    def chain_id(self, obj):
        return obj.chain.chain_id

    @admin.display(ordering="chain__symbol")
    def symbol(self, obj):
        return obj.chain.symbol

    @admin.display(ordering="chain__chain_type")
    def chain_type(self, obj):
        return obj.chain.chain_type


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
        "faucet",
        "user_profile",
        "_status",
        "age",
        last_updated_with_seconds,
    ]
    list_filter = ["faucet", "_status", TXHashFilter]

    def batch__tx_hash(self, obj):
        if obj.batch:
            return obj.batch.tx_hash


class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ["pk", "index", "value"]
    list_editable = ["value"]


class TransactionBatchAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "_status",
        "tx_hash",
        "updating",
        "faucet",
        "age",
        "is_expired",
        "claims_count",
        # "claims_amount",
    ]
    search_fields = ["tx_hash"]
    list_filter = ["faucet", "_status", "updating"]


class LightningConfigAdmin(admin.ModelAdmin):
    readonly_fields = ["claimed_amount", "current_round"]
    list_display = ["pk", "period", "period_max_cap", "claimed_amount", "current_round"]


class DonationReceiptAdmin(admin.ModelAdmin):
    list_display = [
        "tx_hash",
        "user_profile",
        "faucet",
        "value",
        "total_price",
        "datetime",
        "status",
    ]
    search_fields = ["tx_hash"]
    list_filter = ["faucet"]


class DonationContractAdmin(SafeDeleteAdmin):
    list_display = (
        highlight_deleted,
        "contract_address",
        "faucet",
        "datetime",
    ) + SafeDeleteAdmin.list_display
    list_filter = (
        "contract_address",
        SafeDeleteAdminFilter,
    ) + SafeDeleteAdmin.list_filter


admin.site.register(Faucet, FaucetAdmin)
admin.site.register(BrightUser, BrightUserAdmin)
admin.site.register(ClaimReceipt, ClaimReceiptAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)
admin.site.register(TransactionBatch, TransactionBatchAdmin)
admin.site.register(LightningConfig, LightningConfigAdmin)
admin.site.register(DonationReceipt, DonationReceiptAdmin)
admin.site.register(DonationContract, DonationContractAdmin)
