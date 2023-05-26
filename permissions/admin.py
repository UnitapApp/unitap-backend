from django.contrib import admin
from .models import *

# Register your models here.


class BrightIDMeetVerificationAdmin(admin.ModelAdmin):
    list_display = ["pk", "name"]


class BrightIDAuraVerificationAdmin(admin.ModelAdmin):
    list_display = ["pk", "name"]


admin.site.register(BrightIDMeetVerification, BrightIDMeetVerificationAdmin)
admin.site.register(BrightIDAuraVerification, BrightIDAuraVerificationAdmin)