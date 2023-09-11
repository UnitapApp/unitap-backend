from django.contrib import admin
from .models import Mission, Tag, Constraint

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


admin.site.register(Mission, MissionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Constraint, ConstraintAdmin)
