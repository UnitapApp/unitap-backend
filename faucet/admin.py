from django.contrib import admin
from .models import *


class ChainAdmin(admin.ModelAdmin):
    list_display = ['pk', 'chain_name', 'chain_id', 'symbol']


class BrightUserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'address', 'context_id']


class ClaimReceiptAdmin(admin.ModelAdmin):
    list_display = ['pk', 'tx_hash', 'chain', 'bright_user', '_status']


class WalletAccountAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'address']


admin.site.register(WalletAccount, WalletAccountAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(BrightUser, BrightUserAdmin)
admin.site.register(ClaimReceipt, ClaimReceiptAdmin)
