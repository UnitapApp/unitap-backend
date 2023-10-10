from django.contrib import admin
from .models import TokenPrice


class UserConstraintBaseAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'title',
        'type',
        'description',
        'response',
        "icon_url"
    ]
    list_display = [
        "pk",
        "name",
        "description"
    ]


class TokenPriceAdmin(admin.ModelAdmin):
    list_display = [
        'symbol',
        'usd_price',
        'price_url',
        'datetime',
        'last_updated'
    ]
    list_filter = ["symbol"]


admin.site.register(TokenPrice, TokenPriceAdmin)
