from django.contrib import admin

from authentication.models import (
    BrightIDConnection,
    ENSConnection,
    GitcoinPassportConnection,
    TwitterConnection,
    UserProfile,
    Wallet,
    FarcasterConnection,
)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["pk", "username", "initial_context_id", "age"]
    search_fields = [
        "initial_context_id",
        "username",
        "user__auth_token__key",
        "pk",
    ]


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


class GitcoinPassportConnectionAdmin(admin.ModelAdmin):
    list_display = ["pk", "user_profile", "user_wallet_address"]
    search_fields = ["user_wallet_address", "user_profile__username"]


class TwitterConnectionAdmin(admin.ModelAdmin):
    list_display = ["pk", "user_profile", "oauth_token"]
    search_fields = ["user_profile__username", "oauth_token"]


class EnsConnectionAdmin(admin.ModelAdmin):
    list_display = ["pk", "user_profile", "user_wallet_address"]
    search_fields = ["user_profile__username", "user_wallet_address"]


class FarcasterConnectionAdmin(admin.ModelAdmin):
    list_display = ["pk", "user_profile", "user_wallet_address"]
    search_fields = ["user_profile__username", "user_wallet_address"]


admin.site.register(Wallet, WalletAdmin)
admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(BrightIDConnection, BrightIDConnectionAdmin)
admin.site.register(GitcoinPassportConnection, GitcoinPassportConnectionAdmin)
admin.site.register(TwitterConnection, TwitterConnectionAdmin)
admin.site.register(ENSConnection, EnsConnectionAdmin)
admin.site.register(FarcasterConnection, FarcasterConnectionAdmin)
