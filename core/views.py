from collections import defaultdict

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from core.constraints import get_constraint


class AbstractConstraintsListView(ListAPIView):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        constraints = queryset.all()
        response = defaultdict(list)
        for constraint in constraints:
            constraint_obj = get_constraint(constraint.name)
            response[constraint_obj.app_name.value].append(
                self.get_serializer(constraint).data
            )

        return Response(response)
