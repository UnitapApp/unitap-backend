from django.contrib import admin

from authentication.models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["pk", "initial_context_id", "age"]
    search_fields = ["initial_context_id"]


class WalletAdmin(admin.ModelAdmin):
    list_display = ["pk", "wallet_type", "user_profile"]
    search_fields = ["profile__initial_context_id", "wallet_type"]


admin.site.register(Wallet, WalletAdmin)
admin.site.register(UserProfile, ProfileAdmin)
