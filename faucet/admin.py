from django.contrib import admin
from .models import *


class ChainAdmin(admin.ModelAdmin):
    list_display = ['pk', 'chain_name', 'chain_id', 'symbol', 'balance']


class BrightUserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'address', 'context_id', 'verification_status', 'verification_url']


class ClaimReceiptAdmin(admin.ModelAdmin):
    list_display = ['pk', 'tx_hash', 'chain', 'bright_user', 'status']


admin.site.register(Chain, ChainAdmin)
admin.site.register(BrightUser, BrightUserAdmin)
admin.site.register(ClaimReceipt, ClaimReceiptAdmin)
