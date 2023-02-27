from django.contrib import admin

from authentication.models import *

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["pk", "initial_context_id"]
    search_fields = ["initial_context_id"]


admin.site.register(Profile, ProfileAdmin)
