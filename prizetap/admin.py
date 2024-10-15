from django.contrib import admin

from core.admin import UserConstraintBaseAdmin
from prizetap.models import Constraint, LineaRaffleEntries, Raffle, RaffleEntry


class RaffleAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "creator_name", "status"]
    readonly_fields = ["vrf_tx_hash"]
    autocomplete_fields = ["creator_profile"]


class RaffleEntryAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "raffle",
        "user_wallet_address",
        "tx_hash",
        "age",
    ]
    autocomplete_fields = ["wallet_address"]


class LineaRaffleEntriesAdmin(admin.ModelAdmin):
    list_display = ["pk", "wallet_address", "is_winner"]


admin.site.register(Raffle, RaffleAdmin)
admin.site.register(RaffleEntry, RaffleEntryAdmin)
admin.site.register(Constraint, UserConstraintBaseAdmin)
admin.site.register(LineaRaffleEntries, LineaRaffleEntriesAdmin)
