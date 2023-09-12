from .models import *
from rest_framework import serializers
from core.serializers import UserConstraintBaseSerializer


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
            # TODO add user progress if any
        ]
        read_only_fields = [
            "pk",
            "created_at",
        ]


class TaskSerializer(serializers.ModelSerializer):
    verifications = ConstraintSerializer(many=True, read_only=True)

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
            "total_XP",
            "order",
            "has_action",
            "action_button_text",
            "definition",
            "is_active",
            "verifications",
            "verifications_definition",
            "XP",
            # TODO add if is verified or not with data?
        ]


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
            # TODO add user progress if any
        ]
        read_only_fields = [
            "pk",
            "created_at",
        ]
