from django.contrib import admin
from .models import *

# Register your models here.


class BrightIDMeetVerificationAdmin(admin.ModelAdmin):
    list_display = ["pk"]


class BrightIDAuraVerificationAdmin(admin.ModelAdmin):
    list_display = ["pk"]


admin.site.register(BrightIDMeetVerification, BrightIDMeetVerificationAdmin)
admin.site.register(BrightIDAuraVerification, BrightIDAuraVerificationAdmin)
