from django.contrib import admin

from authentication.models import *

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["pk", "initial_context_id"]
    search_fields = ["initial_context_id"]


class EVMWalletAdmin(admin.ModelAdmin):
    list_display = ["pk", "profile", "address", "added_on"]
    search_fields = ["profile", "address"]


class SolanaWalletAdmin(admin.ModelAdmin):
    list_display = ["pk", "profile", "address", "added_on"]
    search_fields = ["profile", "address"]


class BitcoinLightningWalletAdmin(admin.ModelAdmin):
    list_display = ["pk", "profile", "address", "added_on"]
    search_fields = ["profile", "address"]


admin.site.register(EVMWallet, EVMWalletAdmin)
admin.site.register(SolanaWallet, SolanaWalletAdmin)
admin.site.register(BitcoinLightningWallet, BitcoinLightningWalletAdmin)
admin.site.register(Profile, ProfileAdmin)
