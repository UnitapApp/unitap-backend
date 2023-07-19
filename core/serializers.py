from rest_framework import serializers
from .models import UserConstraint

class UserConstraintBaseSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.ChoiceField(
        choices=UserConstraint.Type.choices
    )
    response = serializers.CharField()

    class Meta:
        fields = [
            "pk",
            "name",
            "type",
            "response"
        ]
        read_only_fields = [
            "pk",
            "name",
            "type",
            "response"
        ]