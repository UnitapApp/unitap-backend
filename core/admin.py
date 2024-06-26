from django.contrib import admin

from .models import Chain, Sponsor, TokenPrice, WalletAccount


class UserConstraintBaseAdmin(admin.ModelAdmin):
    fields = [
        "name",
        "title",
        "type",
        "description",
        "negative_description",
        "explanation",
        "response",
        "icon_url",
        "is_active",
    ]
    list_display = ["pk", "name", "description"]


class WalletAccountAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "address"]


class ChainAdmin(admin.ModelAdmin):
    list_display = ["pk", "chain_name", "chain_id", "symbol", "chain_type"]


class TokenPriceAdmin(admin.ModelAdmin):
    list_display = ["symbol", "usd_price", "price_url", "datetime", "last_updated"]
    list_filter = ["symbol"]


class SponsorAdmin(admin.ModelAdmin):
    list_display = ["name", "link"]
    search_fields = ["name"]


admin.site.register(WalletAccount, WalletAccountAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(TokenPrice, TokenPriceAdmin)
admin.site.register(Sponsor, SponsorAdmin)
