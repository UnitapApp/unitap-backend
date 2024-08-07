from django.core.cache import cache
from rest_framework import serializers

from authentication.serializers import SimpleProfilerSerializer
from core.serializers import SponsorSerializer
from quiztap.models import Choice, Competition, Question, UserAnswer, UserCompetition
from quiztap.utils import is_user_eligible_to_participate


class SmallQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("pk", "number")


class CompetitionSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    questions = SmallQuestionSerializer(many=True, read_only=True)
    sponsor = SponsorSerializer(read_only=True)

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
    competition = CompetitionSerializer()
    choices = ChoiceSerializer(many=True)
    is_eligible = serializers.SerializerMethodField(read_only=True)
    remain_participants_count = serializers.SerializerMethodField(read_only=True)
    total_participants_count = serializers.SerializerMethodField(read_only=True)
    amount_won_per_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Question
        fields = "__all__"

    def get_is_eligible(self, ques: Question):
        try:
            user_profile = self.context.get("request").user.profile
        except AttributeError:
            return False
        else:
            return is_user_eligible_to_participate(user_profile, ques.competition)

    def get_remain_participants_count(self, ques: Question):
        remain_participants_count = cache.get(
            f"comp_{ques.competition.pk}_eligible_users_count"
        )
        return (
            remain_participants_count
            if remain_participants_count is not None
            else cache.get(f"comp_{ques.competition.pk}_total_participants_count")
        )

    def get_total_participants_count(self, ques: Question):
        total_participants_count = cache.get(
            f"comp_{ques.competition.pk}_total_participants_count"
        )
        return total_participants_count

    def get_amount_won_per_user(self, ques: Question):
        prize_amount = ques.competition.prize_amount
        remain_participants_count = cache.get(
            f"comp_{ques.competition.pk}_eligible_users_count"
        )
        try:
            prize_amount_per_user = prize_amount / remain_participants_count
            return prize_amount_per_user
        except ZeroDivisionError:
            if (
                ques.competition.is_active
                and ques.competition.can_be_shown
            ):
                return prize_amount
        except TypeError:
            if (
                ques.competition.is_active
                and ques.competition.can_be_shown
            ):
                remain_participants_count = cache.get(
                    f"comp_{ques.competition.pk}_total_participants_count", 1
                )
                return prize_amount / remain_participants_count


class CompetitionField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        pk = super(CompetitionField, self).to_representation(value)
        if self.pk_field is not None:
            return self.pk_field.to_representation(pk)
        try:
            item = Competition.objects.started.get(pk=pk)
            serializer = CompetitionSerializer(item)
            return serializer.data
        except Competition.DoesNotExist:
            return None


class ChoiceField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        pk = super(ChoiceField, self).to_representation(value)
        if self.pk_field is not None:
            return self.pk_field.to_representation(pk)
        try:
            item = Choice.objects.get(pk=pk)
            serializer = ChoiceSerializer(item)
            return serializer.data
        except Choice.DoesNotExist:
            return None


class UserCompetitionSerializer(serializers.ModelSerializer):
    competition = CompetitionField(
        queryset=Competition.objects.not_started.filter(
            is_active=True
        )
    )
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


class UserCompetitionField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        pk = super(UserCompetitionField, self).to_representation(value)
        if self.pk_field is not None:
            return self.pk_field.to_representation(pk)
        try:
            item = UserCompetition.objects.get(pk=pk)
            serializer = UserCompetitionSerializer(item)
            return serializer.data
        except UserCompetition.DoesNotExist:
            return None


class UserAnswerSerializer(serializers.ModelSerializer):
    user_competition = UserCompetitionField(
        queryset=UserCompetition.objects.filter(
            competition__is_active=True,
        )
    )
    selected_choice = ChoiceField(queryset=Choice.objects.all())

    class Meta:
        model = UserAnswer
        fields = "__all__"
