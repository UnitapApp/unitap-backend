from django.contrib import admin

from core.admin import UserConstraintBaseAdmin
from core.models import NetworkTypes
from prizetap.models import Constraint, LineaRaffleEntries, Raffle, RaffleEntry


class RaffleAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "creator_name", "status"]


class RaffleٍEntryAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "raffle",
        "get_wallet",
        "age",
    ]

    @admin.display(ordering="user_profile__wallets", description="Wallet")
    def get_wallet(self, obj):
        return obj.user_profile.wallets.get(wallet_type=NetworkTypes.EVM).address


class LineaRaffleEntriesAdmin(admin.ModelAdmin):
    list_display = ["pk", "wallet_address", "is_winner"]


admin.site.register(Raffle, RaffleAdmin)
admin.site.register(RaffleEntry, RaffleٍEntryAdmin)
admin.site.register(Constraint, UserConstraintBaseAdmin)
admin.site.register(LineaRaffleEntries, LineaRaffleEntriesAdmin)
