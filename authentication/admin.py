from django.contrib import admin

from authentication.models import BrightIDConnection, UserProfile, Wallet


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["pk", "initial_context_id", "age"]
    search_fields = ["initial_context_id", "user__auth_token__key", "user__pk"]


class WalletAdmin(admin.ModelAdmin):
    list_display = ["pk", "wallet_type", "user_profile"]
    search_fields = [
        "user_profile__initial_context_id",
        "wallet_type",
        "address",
        "user_profile__pk",
        "user_profile__user__auth_token__key",
    ]


class BrightIDConnectionAdmin(admin.ModelAdmin):
    list_display = ["pk", "user_profile", "context_id", "age"]
    search_fields = [
        "context_id",
    ]


admin.site.register(Wallet, WalletAdmin)
admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(BrightIDConnection, BrightIDConnectionAdmin)
