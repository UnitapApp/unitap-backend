from django.contrib import admin
from .models import *

# Register your models here.


class MissionAdmin(admin.ModelAdmin):
    list_display = ("title", "creator_name", "created_at", "is_active", "is_promoted")
    list_filter = ("is_active", "is_promoted")
    search_fields = ("title", "creator_name")
    list_editable = ("is_active", "is_promoted")


class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ConstraintAdmin(admin.ModelAdmin):
    list_display = ("name",)


class StationAdmin(admin.ModelAdmin):
    list_display = ("title", "mission", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "mission__title")
    list_editable = ("is_active",)


class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "station", "mission", "is_active")
    list_filter = ("is_active", "mission", "station")
    search_fields = ("title", "station__title", "mission__title")
    list_editable = ("is_active",)


admin.site.register(Mission, MissionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Constraint, ConstraintAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Task, TaskAdmin)
