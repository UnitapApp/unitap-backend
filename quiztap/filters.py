from rest_framework import filters
from rest_framework.generics import get_object_or_404

from quiztap.models import Competition


class CompetitionFilter(filters.BaseFilterBackend):
    """
    Filter with competition_pk
    """

    def filter_queryset(self, request, queryset, view):
        competition_pk = request.query_params.get("competition_pk")
        if competition_pk is None:
            return queryset
        return queryset.filter(
            competition=get_object_or_404(Competition, pk=competition_pk)
        )


class NestedCompetitionFilter(filters.BaseFilterBackend):
    """
    Filter with competition_pk
    """

    def filter_queryset(self, request, queryset, view):
        competition_pk = request.query_params.get("competition_pk")
        if competition_pk is None:
            return queryset
        return queryset.filter(
            user_competition__competition=get_object_or_404(
                Competition, pk=competition_pk
            )
        )
