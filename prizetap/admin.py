from django.contrib import admin
from prizetap.models import *


class RaffleAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "creator"]


admin.site.register(Raffle, RaffleAdmin)
