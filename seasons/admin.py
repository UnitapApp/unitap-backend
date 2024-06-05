from django.contrib import admin

from .models import Season, SeasonLevel, XPRecord


class SeasonAdmin(admin.ModelAdmin):
    list_display = ["name", "start_date", "end_date", "sponsor", "status"]


class RecordAdmin(admin.ModelAdmin):
    list_display = ["context", "xp", "user", "created_at"]


class SeasonLevelAdmin(admin.ModelAdmin):
    list_display = ["season", "required_xp"]


admin.site.register(Season, SeasonAdmin)
admin.site.register(SeasonLevel, SeasonLevelAdmin)
admin.site.register(XPRecord, RecordAdmin)
