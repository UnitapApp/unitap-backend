from django.core.validators import FileExtensionValidator
from drf_yasg import openapi
from drf_yasg.inspectors import InlineSerializerInspector
from rest_framework import serializers


class ConstraintProviderSrializerInspector(InlineSerializerInspector):
    def get_request_parameters(self, serializer, in_):
        fields = getattr(serializer, "fields", {})
        parameters = [
            self.probe_field_inspectors(
                value,
                openapi.Parameter,
                self.use_definitions,
                name=self.get_parameter_name(key),
                in_=in_,
            )
            for key, value in fields.items()
            if not getattr(value, "read_only", False) and key != "constraint_files"
        ]
        parameters.append(
            self.probe_field_inspectors(
                serializers.FileField(
                    allow_empty_file=False, validators=[FileExtensionValidator(["csv"])]
                ),
                openapi.Parameter,
                self.use_definitions,
                name="constraint_files",
                in_=in_,
            )
        )

        return parameters
