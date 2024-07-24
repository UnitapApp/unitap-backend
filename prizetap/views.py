import json

import rest_framework.exceptions
from django.db import transaction
from django.db.models import Case, F, When
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from web3 import Web3

from authentication.models import UserProfile
from core.constraints import ConstraintVerification, get_constraint
from core.models import Chain
from core.paginations import StandardResultsSetPagination
from core.serializers import ChainSerializer
from core.swagger import ConstraintProviderSrializerInspector
from core.views import AbstractConstraintsListView

from .constants import CONTRACT_ADDRESSES
from .models import Constraint, LineaRaffleEntries, Raffle, RaffleEntry
from .serializers import (
    ConstraintSerializer,
    CreateRaffleSerializer,
    LineaRaffleEntrySerializer,
    RaffleEntrySerializer,
    RaffleSerializer,
)
from .validators import (
    RaffleEnrollmentValidator,
    SetClaimingPrizeTxValidator,
    SetRaffleEntryTxValidator,
    SetRaffleTxValidator,
)


class RaffleListView(ListAPIView):
    now = timezone.now()
    valid_time = now - timezone.timedelta(days=360)
    queryset = (
        Raffle.objects.filter(is_active=True)
        .filter(deadline__gte=valid_time)
        .annotate(
            is_expired_true=Case(
                When(deadline__gte=now, then=("deadline")), default=None
            ),
            is_expired_false=Case(When(deadline__lt=now, then=("pk")), default=None),
        )
        .order_by("-is_expired_false", "-is_expired_true")
    )
    serializer_class = RaffleSerializer

    def get(self, request):
        queryset = self.get_queryset()
        if request.user.is_authenticated:
            RaffleEntry.set_entry_user_profiles(request.user)
        serializer = RaffleSerializer(
            queryset,
            many=True,
            context={
                "user": request.user.profile if request.user.is_authenticated else None
            },
        )
        return Response(serializer.data)


class RaffleEnrollmentView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_profile: UserProfile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=pk)
        if raffle.pre_enrollment_wallets:
            raise rest_framework.exceptions.ValidationError("Raffle is pre-enrollment")
        user_wallet_address = request.data.get("user_wallet_address", None)
        raffle_data = request.data.get("raffle_data", None)
        if not user_wallet_address:
            raise rest_framework.exceptions.ParseError(
                "user_wallet_address is required"
            )

        validator = RaffleEnrollmentValidator(
            user_profile=user_profile, raffle=raffle, raffle_data=raffle_data
        )

        validator.is_valid(self.request.data)
        prizetap_winning_chance_number = int(
            self.request.data.get("prizetap_winning_chance_number", 0)
        )

        try:
            raffle_entry = raffle.entries.get(user_profile=user_profile)
        except RaffleEntry.DoesNotExist:
            with transaction.atomic():
                user_profile.prizetap_winning_chance_number = (
                    F("prizetap_winning_chance_number") - prizetap_winning_chance_number
                )
                user_profile.save(update_fields=("prizetap_winning_chance_number",))
                raffle_entry = RaffleEntry.objects.create(
                    user_profile_id=user_profile.pk,
                    user_wallet_address=Web3.to_checksum_address(user_wallet_address),
                    raffle=raffle,
                    multiplier=prizetap_winning_chance_number + 1,
                )
                raffle_entry.save()

        return Response(
            {
                "detail": "Enrolled Successfully",
                "signature": RaffleEntrySerializer(raffle_entry).data,
            },
            status=200,
        )


class SetEnrollmentTxView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle_entry = get_object_or_404(RaffleEntry, pk=pk)

        validator = SetRaffleEntryTxValidator(
            user_profile=user_profile, raffle_entry=raffle_entry
        )

        validator.is_valid(self.request.data)

        tx_hash = self.request.data.get("tx_hash", None)
        raffle_entry.tx_hash = tx_hash
        raffle_entry.save()

        return Response(
            {
                "detail": "Raffle entry updated successfully",
                "success": True,
                "entry": RaffleEntrySerializer(raffle_entry).data,
            },
            status=200,
        )


class SetClaimingPrizeTxView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=pk)
        raffle_entry = get_object_or_404(
            RaffleEntry, raffle=raffle, user_profile=user_profile
        )

        validator = SetClaimingPrizeTxValidator(
            user_profile=user_profile, raffle_entry=raffle_entry
        )

        validator.is_valid(self.request.data)

        tx_hash = self.request.data.get("tx_hash", None)
        raffle_entry.claiming_prize_tx = tx_hash
        raffle_entry.save()

        return Response(
            {
                "detail": "Raffle entry updated successfully",
                "success": True,
                "entry": RaffleEntrySerializer(raffle_entry).data,
            },
            status=200,
        )


class GetRaffleEntryView(APIView):
    def get(self, request, pk):
        raffle_entry = get_object_or_404(RaffleEntry, pk=pk)

        return Response(
            {"success": True, "entry": RaffleEntrySerializer(raffle_entry).data},
            status=200,
        )


class GetRaffleConstraintsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, raffle_pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=raffle_pk)
        try:
            param_values = json.loads(raffle.constraint_params)
        except Exception:
            param_values = {}

        reversed_constraints = raffle.reversed_constraints_list
        response_constraints = []

        for c in raffle.constraints.all():
            constraint: ConstraintVerification = get_constraint(c.name)(user_profile)
            constraint.response = c.response
            try:
                constraint.param_values = param_values[c.name]
            except KeyError:
                pass
            is_verified = False
            if str(c.pk) in reversed_constraints:
                if not constraint.is_observed():
                    is_verified = True
            else:
                if constraint.is_observed():
                    is_verified = True
            response_constraints.append(
                {
                    **ConstraintSerializer(c).data,
                    "is_verified": is_verified,
                    "is_reversed": True if str(c.pk) in reversed_constraints else False,
                }
            )

        return Response(
            {"success": True, "constraints": response_constraints}, status=200
        )


class CreateRaffleView(CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    serializer_class = CreateRaffleSerializer

    @swagger_auto_schema(field_inspectors=[ConstraintProviderSrializerInspector])
    def post(self, request: Request):
        serializer: CreateRaffleSerializer = self.get_serializer(
            data=request.data, context={"user_profile": request.user.profile}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data})


class SetRaffleTXView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=pk)

        validator = SetRaffleTxValidator(user_profile=user_profile, raffle=raffle)

        validator.is_valid(self.request.data)

        tx_hash = self.request.data.get("tx_hash", None)
        raffle.tx_hash = tx_hash
        raffle.save()

        return Response(
            {
                "detail": "Raffle updated successfully",
                "success": True,
                "raffle": RaffleSerializer(
                    raffle, context={"user": request.user.profile}
                ).data,
            },
            status=200,
        )


class ValidChainsView(ListAPIView):
    queryset = Chain.objects.filter(
        chain_id__in=list(CONTRACT_ADDRESSES.keys())
    ).order_by("pk")
    serializer_class = ChainSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = ChainSerializer(queryset, many=True)
        response = []
        for chain in serializer.data:
            response.append({**chain, **CONTRACT_ADDRESSES[chain["chain_id"]]})
        return Response({"success": True, "data": response})


class UserRafflesListView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Raffle.objects.filter(creator_profile=request.user.profile).order_by(
            "-pk"
        )
        serializer = RaffleSerializer(
            queryset, many=True, context={"user": request.user.profile}
        )
        return Response(serializer.data)


class ConstraintsListView(AbstractConstraintsListView):
    queryset = Constraint.objects.filter(is_active=True)
    serializer_class = ConstraintSerializer


class LineaRaffleView(ListAPIView):
    serializer_class = LineaRaffleEntrySerializer

    def get_queryset(self):
        return LineaRaffleEntries.objects.all()


class SetLineaTxHashView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        tx_hash = request.data.get("tx_hash")
        raffle_entry = get_object_or_404(LineaRaffleEntries, pk=pk)
        raffle_entry.claim_tx = tx_hash
        raffle_entry.save()
        return Response(
            {"success": True, "data": LineaRaffleEntrySerializer(raffle_entry).data}
        )


class RaffleDetailsView(RetrieveAPIView):
    serializer_class = RaffleSerializer

    def get(self, request: Request, pk):
        queryset = Raffle.objects.get(pk=pk)
        serializer = RaffleSerializer(
            queryset,
            context={
                "user": request.user.profile if request.user.is_authenticated else None
            },
        )
        return Response(serializer.data)


class RaffleEntriesView(ListAPIView):
    pagination_class = StandardResultsSetPagination
    serializer_class = RaffleEntrySerializer

    def get_queryset(self, *args, **kwargs):
        raffle_pk = self.request.parser_context.get("kwargs").get("pk")
        return RaffleEntry.objects.filter(raffle__pk=raffle_pk).order_by("pk")
