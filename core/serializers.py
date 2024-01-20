import base64
import json

from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from core.constraints import ConstraintVerification, get_constraint

from .models import Chain, UserConstraint
from .utils import UploadFileStorage


class ChainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chain
        ref_name = "core-chain"  # temporary
        fields = [
            "pk",
            "chain_name",
            "chain_id",
            "native_currency_name",
            "symbol",
            "decimals",
            "explorer_url",
            "rpc_url",
            "logo_url",
            "modal_url",
            "is_testnet",
            "chain_type",
        ]


class UserConstraintBaseSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    name = serializers.CharField()
    title = serializers.CharField()
    type = serializers.ChoiceField(choices=UserConstraint.Type.choices)
    description = serializers.CharField()
    explanation = serializers.CharField()
    response = serializers.CharField()
    icon_url = serializers.CharField()
    params = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "pk",
            "name",
            "title",
            "type",
            "description",
            "negative_description",
            "explanation",
            "response",
            "icon_url",
            "params",
        ]
        read_only_fields = [
            "pk",
            "name",
            "title",
            "type",
            "description",
            "negative_description",
            "explanation",
            "response",
            "icon_url",
            "params",
        ]

    def get_params(self, constraint: UserConstraint):
        c_class: ConstraintVerification = get_constraint(constraint.name)
        return [p.name for p in c_class.param_keys()]


class ConstraintProviderSerializer(serializers.Serializer):
    constraint_files = serializers.ListField(
        required=False,
        child=serializers.FileField(
            allow_empty_file=False, validators=[FileExtensionValidator(["csv"])]
        ),
    )

    class Meta:
        abstract = True

    def validate(self, data):
        constraints = data["constraints"]
        if "constraint_params" in data:
            data["constraint_params"] = base64.b64decode(
                data["constraint_params"]
            ).decode("utf-8")
        else:
            data["constraint_params"] = "{}"
        constraint_params = json.loads(data["constraint_params"])
        reversed_constraints = []
        if "reversed_constraints" in data:
            reversed_constraints = str(data["reversed_constraints"]).split(",")
        if len(constraints) != 0:
            for c in constraints:
                constraint_class: ConstraintVerification = get_constraint(c.name)
                try:
                    if len(constraint_class.param_keys()) != 0:
                        constraint_class.is_valid_param_keys(constraint_params[c.name])
                except KeyError as e:
                    # TODO: revise errors
                    raise serializers.ValidationError(
                        {"constraint_params": [{f"{c.name}": str(e)}]}
                    )
        valid_constraints = [str(c.pk) for c in constraints]
        for c in reversed_constraints:
            if c not in valid_constraints:
                raise serializers.ValidationError(
                    {"reversed_constraints": [{f"{c}": "Invalid constraint pk"}]}
                )
        if "constraint_files" in data:
            file_names = [file.name for file in data["constraint_files"]]
            if len(file_names) != len(set(file_names)):
                raise serializers.ValidationError(
                    {"constraint_files": "The name of files should be unique"}
                )
        return data

    def save_constraint_files(self, validated_data):
        if "constraint_files" in validated_data:
            constraint_files = validated_data.pop("constraint_files")
            constraint_params = json.loads(validated_data.get("constraint_params"))
            file_storage = UploadFileStorage()
            for ـ, constraint in constraint_params.items():
                if "CSV_FILE" not in constraint:
                    continue
                file_exist = False
                for file in constraint_files:
                    if constraint["CSV_FILE"] == file.name:
                        path = file_storage.save(file)
                        constraint["CSV_FILE"] = path
                        file_exist = True
                        break
                if not file_exist:
                    raise serializers.ValidationError(
                        {
                            "constraint_files": (
                                f'File {constraint["CSV_FILE"]} is not exist'
                            )
                        }
                    )
            validated_data["constraint_params"] = json.dumps(constraint_params)
        return validated_data
