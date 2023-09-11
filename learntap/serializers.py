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
