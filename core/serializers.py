from rest_framework import serializers
from .constraints import *
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
    params = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "pk",
            "name",
            "title",
            "type",
            "description",
            "response",
            "params"
        ]
        read_only_fields = [
            "pk",
            "name",
            "title",
            "type",
            "description",
            "response",
            "params"
        ]

    def get_params(self, constraint: UserConstraint):
        c_class: ConstraintVerification = eval(constraint.name)
        return [p.name for p in c_class.param_keys()]