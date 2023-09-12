from .models import *
from rest_framework import serializers
from core.serializers import UserConstraintBaseSerializer
from .helpers import UserProgressManager


class ConstraintSerializer(UserConstraintBaseSerializer, serializers.ModelSerializer):
    class Meta(UserConstraintBaseSerializer.Meta):
        ref_name = "MissionConstraint"
        model = Constraint


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class MissionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    constraints = ConstraintSerializer(many=True, read_only=True)
    has_completed_mission = serializers.SerializerMethodField()
    is_in_progress = serializers.SerializerMethodField()
    mission_progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = [
            "pk",
            "title",
            "creator_name",
            "creator_url",
            "discord_url",
            "twitter_url",
            "description",
            "imageUrl",
            "is_promoted",
            "is_active",
            "tags",
            "constraints",
            "constraint_params",
            "created_at",
            "total_XP",
            "has_completed_mission",
            "is_in_progress",
            "mission_progress_percentage",
        ]
        read_only_fields = [
            "pk",
            "created_at",
        ]

    def get_has_completed_mission(self, obj):
        try:
            if not self.context["request"].user.is_authenticated:
                return False
            return UserProgressManager.has_completed_mission(
                self.context["request"].user.profile, obj
            )
        except UserMissionProgress.DoesNotExist or UserTaskProgress.DoesNotExist:
            return False

    def get_is_in_progress(self, obj):
        try:
            if not self.context["request"].user.is_authenticated:
                return False
            return UserProgressManager.has_started_mission(
                self.context["request"].user.profile, obj
            )
        except UserMissionProgress.DoesNotExist or UserTaskProgress.DoesNotExist:
            return False

    def get_mission_progress_percentage(self, obj):
        try:
            if not self.context["request"].user.is_authenticated:
                return 0
            return UserProgressManager.get_user_mission_progress_percentage(
                self.context["request"].user.profile, obj
            )
        except UserMissionProgress.DoesNotExist or UserTaskProgress.DoesNotExist:
            return 0


class TaskSerializer(serializers.ModelSerializer):
    verifications = ConstraintSerializer(many=True, read_only=True)
    is_verified = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "pk",
            "station",
            "mission",
            "title",
            "description",
            "imageUrl",
            "is_active",
            "order",
            "has_action",
            "action_button_text",
            "definition",
            "is_active",
            "verifications",
            "verifications_definition",
            "XP",
            "is_verified",
        ]

    def get_is_verified(self, obj):
        try:
            if not self.context["request"].user.is_authenticated:
                return False
            return UserProgressManager.has_completed_task(
                self.context["request"].user.profile, obj
            )
        except UserMissionProgress.DoesNotExist or UserTaskProgress.DoesNotExist:
            return False


class StationSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Station
        fields = [
            "pk",
            "mission",
            "title",
            "description",
            "imageUrl",
            "is_active",
            "total_XP",
            "tasks",
            "order",
        ]


class MissionFullSerializer(serializers.ModelSerializer):
    stations = StationSerializer(many=True, read_only=True)
    has_completed_mission = serializers.SerializerMethodField()
    is_in_progress = serializers.SerializerMethodField()
    mission_progress_percentage = serializers.SerializerMethodField()
    current_task = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    constraints = ConstraintSerializer(many=True, read_only=True)

    class Meta:
        model = Mission
        fields = [
            "pk",
            "title",
            "creator_name",
            "creator_url",
            "discord_url",
            "twitter_url",
            "description",
            "imageUrl",
            "is_promoted",
            "is_active",
            "tags",
            "constraints",
            "constraint_params",
            "created_at",
            "total_XP",
            "stations",
            "has_completed_mission",
            "is_in_progress",
            "mission_progress_percentage",
            "current_task",
        ]
        read_only_fields = [
            "pk",
            "created_at",
        ]

    def get_current_task(self, obj):
        try:
            if not self.context["request"].user.is_authenticated:
                return None
            if UserProgressManager.has_completed_mission(
                self.context["request"].user.profile, obj
            ):
                return None
            return TaskSerializer(
                UserProgressManager.get_current_task_of_mission(
                    self.context["request"].user.profile, obj
                ),
                context=self.context,
            ).data
        except UserMissionProgress.DoesNotExist or UserTaskProgress.DoesNotExist:
            return None

    def get_has_completed_mission(self, obj):
        try:
            if not self.context["request"].user.is_authenticated:
                return False
            return UserProgressManager.has_completed_mission(
                self.context["request"].user.profile, obj
            )
        except UserMissionProgress.DoesNotExist or UserTaskProgress.DoesNotExist:
            return False

    def get_is_in_progress(self, obj):
        try:
            if not self.context["request"].user.is_authenticated:
                return False
            return UserProgressManager.has_started_mission(
                self.context["request"].user.profile, obj
            )
        except UserMissionProgress.DoesNotExist or UserTaskProgress.DoesNotExist:
            return False

    def get_mission_progress_percentage(self, obj):
        try:
            if not self.context["request"].user.is_authenticated:
                return 0
            return UserProgressManager.get_user_mission_progress_percentage(
                self.context["request"].user.profile, obj
            )
        except UserMissionProgress.DoesNotExist or UserTaskProgress.DoesNotExist:
            return 0
