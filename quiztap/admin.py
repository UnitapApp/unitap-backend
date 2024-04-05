from django.contrib import admin

from quiztap.models import Choice, Competition, Question

# Create your views here.


class CompetitionAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "details",
        "status",
        "username",
        "chain_name",
        "token",
    )

    search_fields = ("chain_name", "status", "user_profile", "pk")
    list_filter = ("status", "chain_name")

    @admin.display(ordering="chain__chain_name")
    def chain_name(self, obj):
        return obj.chain.chain_name

    @admin.display(ordering="user_profile__username")
    def username(self, obj):
        return obj.user_profile.uesrname


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "number",
        "competition",
        "answer_time_limit_seconds",
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
