from django.contrib import admin

from quiztap.models import Choice, Competition, Question


class CompetitionAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "details",
        "details",
        "status",
        "username",
        "chain_name",
        "token",
    )

    search_fields = ("status", "user_profile", "pk")
    list_filter = ("status",)

    @admin.display(ordering="chain__chain_name")
    def chain_name(self, obj):
        return obj.chain.chain_name

    @admin.display(ordering="user_profile__username")
    def username(self, obj):
        return obj.user_profile.username


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "number",
        "competition",
    )

    list_filter = ("competition", "text")
    search_fields = ("competition", "number", "pk")


class ChoiceAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "question",
        "is_correct",
    )

    list_filter = ("question", "text")
    search_fields = ("question", "pk")


admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
