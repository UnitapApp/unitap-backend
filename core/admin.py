from django.contrib import admin

class UserConstraintBaseAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'title',
        'type',
        'description',
        'response'
    ]
    list_display = [
        "pk",
        "name",
        "description"
    ]