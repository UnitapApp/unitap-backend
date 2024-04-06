from rest_framework import serializers

from authentication.serializers import SimpleProfilerSerializer
from quiztap.models import Choice, Competition, Question, UserAnswer, UserCompetition


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
    is_correct = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = "__all__"

    def get_is_correct(self, choice: Choice):
        if choice.question.answer_can_be_shown:
            return choice.is_correct


class QuestionSerializer(serializers.ModelSerializer):
    competition = ChoiceSerializer()
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = "__all__"


class CompetitionField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)
        return CompetitionSerializer(instance=value).data


class ChoiceField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)
        return CompetitionSerializer(instance=value).data


class UserCompetitionSerializer(serializers.ModelSerializer):
    competition = CompetitionField(queryset=Competition.objects.filter(is_active=True))
    user_profile = SimpleProfilerSerializer(read_only=True)

    class Meta:
        model = UserCompetition
        fields = "__all__"
        read_only_fields = [
            "pk",
            "user_profile",
            "is_winner",
            "amount_won",
        ]


class UserAnswerSerializer(serializers.ModelSerializer):
    competition = CompetitionField(queryset=Competition.objects.filter(is_active=True))
    selected_choice = ChoiceField(queryset=Competition.objects.all())

    class Meta:
        model = UserAnswer
        fields = "__all__"
