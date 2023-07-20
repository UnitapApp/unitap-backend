from rest_framework import serializers
from .models import UserConstraint

class UserConstraintBaseSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    name = serializers.CharField()
    title = serializers.CharField()
    type = serializers.ChoiceField(
        choices=UserConstraint.Type.choices
    )
    description = serializers.CharField()
    response = serializers.CharField()

    class Meta:
        fields = [
            "pk",
            "name",
            "title",
            "type",
            "description",
            "response"
        ]
        read_only_fields = [
            "pk",
            "name",
            "title",
            "type",
            "description",
            "response"
        ]