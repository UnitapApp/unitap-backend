from django.shortcuts import get_object_or_404
from rest_framework import filters

from .models import Faucet


class FaucetFilterBackend(filters.BaseFilterBackend):
    """
    Filter that filter nested faucet
    """

    def filter_queryset(self, request, queryset, view):
        faucet_pk = request.query_params.get("faucet_pk")
        if faucet_pk is None:
            return queryset
        return queryset.filter(faucet=get_object_or_404(Faucet, pk=faucet_pk))
