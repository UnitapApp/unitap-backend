from rest_framework import serializers

from quiztap.models import Choice, Competition, Question


class SmallQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("pk", "number")


class CompetitionSerializer(serializers.ModelSerializer):
    username = serializers.ModelSerializer(read_only=True)
    questions = SmallQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Competition
        exclude = (
            "user_profile",
            "participants",
        )

    def get_username(self, comp: Competition):
        return comp.user_profile.username


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        exclude = ("is_correct",)


class QuestionSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer()
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = "__all__"
