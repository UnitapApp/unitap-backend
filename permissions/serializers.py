from rest_framework import serializers
from rest_framework_polymorphic.serializers import PolymorphicSerializer


from permissions.models import (
    Permission,
    BrightIDMeetVerification,
    BrightIDAuraVerification,
)


class PermissionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "description"]


class BrightIDMeetVerificationSerializer(PermissionBaseSerializer):
    class Meta:
        model = BrightIDMeetVerification
        fields = ["id", "name", "description"]


class BrightIDAuraVerificationSerializer(PermissionBaseSerializer):
    class Meta:
        model = BrightIDAuraVerification
        fields = ["id", "name", "description"]


class PermissionSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Permission: PermissionBaseSerializer,
        BrightIDMeetVerification: BrightIDMeetVerificationSerializer,
        BrightIDAuraVerification: BrightIDAuraVerificationSerializer,
    }
