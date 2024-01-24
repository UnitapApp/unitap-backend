import datetime
import json
import os

import pytz
import rest_framework.exceptions
from django.conf import settings
from django.contrib.postgres.expressions import ArraySubquery
from django.core.cache import cache
from django.db.models import F, FloatField, OuterRef, Subquery, Sum
from django.db.models.functions import Cast
from django.http import FileResponse, Http404, HttpResponse
from django.urls import reverse
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import UserProfile
from core.filters import IsOwnerFilterBackend
from core.paginations import StandardResultsSetPagination
from core.validators import address_validator
from faucet.faucet_manager.claim_manager import (
    ClaimManagerFactory,
    LimitedChainClaimManager,
)
from faucet.faucet_manager.credit_strategy import RoundCreditStrategy
from faucet.filters import FaucetFilterBackend
from faucet.models import ClaimReceipt, DonationReceipt, Faucet, GlobalSettings
from faucet.serializers import (
    DonationReceiptSerializer,
    FaucetBalanceSerializer,
    FaucetSerializer,
    FuelChampionSerializer,
    GlobalSettingsSerializer,
    LeaderboardSerializer,
    ReceiptSerializer,
    SmallFaucetSerializer,
)


class CustomException(Exception):
    pass


class ClaimCountView(ListAPIView):
    def get(self, request, *args, **kwargs):
        return Response({"count": ClaimReceipt.claims_count()}, status=200)


class LastClaimView(RetrieveAPIView):
    serializer_class = ReceiptSerializer

    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_profile = self.request.user.profile
        try:
            return (
                ClaimReceipt.objects.filter(user_profile=user_profile)
                .order_by("pk")
                .last()
            )
        except ClaimReceipt.DoesNotExist:
            raise Http404("Claim Receipt for this user does not exist")


class ListClaims(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptSerializer

    def get_queryset(self):
        user_profile = self.request.user.profile
        return ClaimReceipt.objects.filter(
            user_profile=user_profile,
            _status__in=[
                ClaimReceipt.VERIFIED,
                ClaimReceipt.PENDING,
                ClaimReceipt.REJECTED,
            ],
            datetime__gte=RoundCreditStrategy.get_start_of_the_round(),
        ).order_by("-pk")


class ListOneTimeClaims(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptSerializer

    def get_queryset(self):
        user_profile = self.request.user.profile
        return ClaimReceipt.objects.filter(
            user_profile=user_profile,
            faucet__in=Faucet.objects.filter(is_one_time_claim=True),
            _status__in=[
                ClaimReceipt.VERIFIED,
                ClaimReceipt.PENDING,
                ClaimReceipt.REJECTED,
            ],
            # 18 December 2023
            datetime__gte=datetime.datetime(
                2023, 12, 18, 0, 0, 0, 0, pytz.timezone("UTC")
            ),  # also change in credit_strategy.py
        ).order_by("-pk")


class GetTotalRoundClaimsRemainingView(RetrieveAPIView):
    """
    Return the total weekly claims remaining for the given user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        gs = GlobalSettings.objects.first()
        if gs is not None:
            result = max(
                gs.gastap_round_claim_limit
                - LimitedChainClaimManager.get_total_round_claims(user_profile),
                0,
            )
            return Response({"total_round_claims_remaining": result}, status=200)
        else:
            raise Http404("Global Settings Not Found")


class FaucetListView(ListAPIView):
    """
    list of faucets

    this endpoint returns detailed user specific info if supplied with an address
    """

    serializer_class = FaucetSerializer

    def get_queryset(self):
        queryset = Faucet.objects.filter(is_active=True, show_in_gastap=True)

        sorted_queryset = sorted(
            queryset, key=lambda obj: obj.total_claims_since_last_round, reverse=True
        )
        return sorted_queryset


class SmallFaucetListView(ListAPIView):
    """
    list of faucet with minimum details
    """

    serializer_class = SmallFaucetSerializer
    queryset = Faucet.objects.filter(is_active=True, show_in_gastap=True)


class GlobalSettingsView(RetrieveAPIView):
    serializer_class = GlobalSettingsSerializer

    def get_object(self):
        return GlobalSettings.objects.first()


# TODO: fixme
class ClaimMaxView(APIView):
    """
    Claims maximum possible fee for the given user and faucet

    **user must be verified**
    """

    permission_classes = [IsAuthenticated]

    def get_user(self) -> UserProfile:
        return self.request.user.profile

    def check_user_is_verified(self, type="Meet"):
        _is_verified = self.get_user().is_meet_verified
        # _is_verified = True
        if not _is_verified:
            # return Response({"message": "You are not BrighID verified"}, status=403)
            raise rest_framework.exceptions.PermissionDenied(
                "You are not BrighID verified"
            )

    def to_address_is_provided(self):
        to_address = self.request.data.get("address", None)
        if not to_address:
            raise rest_framework.exceptions.ParseError("wallet address not set")

    def get_faucet(self) -> Faucet:
        faucet_pk = self.kwargs.get("faucet_pk", None)
        try:
            return Faucet.objects.get(pk=faucet_pk)
        except Faucet.DoesNotExist:
            raise Http404(f"Faucet with id {faucet_pk} Does not Exist")

    def get_claim_manager(self):
        return ClaimManagerFactory(self.get_faucet(), self.get_user()).get_manager()

    def check_to_address_is_validate(self):
        chain = self.get_faucet().chain
        to_address = self.request.data.get("address", None)
        address_validator(to_address, chain)

    def claim_max(self, to_address) -> ClaimReceipt:
        manager = self.get_claim_manager()
        max_credit = manager.get_credit_strategy().get_unclaimed()
        try:
            assert max_credit > 0
            return manager.claim(max_credit, to_address=to_address)
        except AssertionError:
            raise rest_framework.exceptions.PermissionDenied("Something Went Wrong")
        except ValueError as e:
            raise rest_framework.exceptions.APIException(e)

    def post(self, request, *args, **kwargs):
        self.check_user_is_verified()
        self.to_address_is_provided()
        self.check_to_address_is_validate()

        receipt = self.claim_max(to_address=request.data.get("address"))
        return Response(ReceiptSerializer(instance=receipt).data)


class FaucetBalanceView(RetrieveAPIView):
    serializer_class = FaucetBalanceSerializer

    def get_object(self):
        faucet_pk = self.kwargs.get("faucet_pk", None)
        if faucet_pk is None:
            raise Http404("Faucet ID not provided")
        return Faucet.objects.get(pk=faucet_pk)


class DonationReceiptView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DonationReceiptSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [IsOwnerFilterBackend, FaucetFilterBackend]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.get_user()})
        return context

    def get_queryset(self):
        return DonationReceipt.objects.all().order_by("-datetime")

    def get_user(self) -> UserProfile:
        return self.request.user.profile


class UserLeaderboardView(RetrieveAPIView):
    filter_backends = [FaucetFilterBackend]
    permission_classes = [IsAuthenticated]
    queryset = DonationReceipt.objects.all()
    serializer_class = LeaderboardSerializer

    def get_user(self) -> UserProfile:
        return self.request.user.profile

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = (
            queryset.filter(status=ClaimReceipt.VERIFIED)
            .annotate(total_price_float=Cast("total_price", FloatField()))
            .values("user_profile")
            .annotate(sum_total_price=Sum("total_price_float"))
        )
        user_obj = get_object_or_404(queryset, user_profile=self.get_user().pk)
        user_rank = (
            queryset.filter(sum_total_price__gt=user_obj.get("sum_total_price")).count()
            + 1
        )
        user_obj["rank"] = user_rank
        user_obj["username"] = self.get_user().username
        interacted_chains = list(
            DonationReceipt.objects.filter(user_profile=self.get_user())
            .filter(status=ClaimReceipt.VERIFIED)
            .values_list("faucet__chain", flat=True)  # TODO fixme
            .distinct()
        )
        user_obj["interacted_chains"] = interacted_chains

        return user_obj


class LeaderboardView(ListAPIView):
    serializer_class = LeaderboardSerializer
    pagination_class = StandardResultsSetPagination
    queryset = DonationReceipt.objects.all()
    filter_backends = [FaucetFilterBackend]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        donation_receipt = (
            queryset.filter(status=ClaimReceipt.VERIFIED)
            .annotate(total_price_float=Cast("total_price", FloatField()))
            .values("user_profile")
            .annotate(sum_total_price=Sum("total_price_float"))
            .order_by("-sum_total_price")
        )
        subquery_interacted_chains = (
            DonationReceipt.objects.filter(user_profile=OuterRef("user_profile"))
            .filter(status=ClaimReceipt.VERIFIED)
            .values_list("faucet__chain", flat=True)
            .distinct()
        )
        queryset = donation_receipt.annotate(
            interacted_chains=ArraySubquery(subquery_interacted_chains)
        )
        subquery_username = UserProfile.objects.filter(
            pk=OuterRef("user_profile")
        ).values("username")
        queryset = queryset.annotate(username=Subquery(subquery_username))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FuelChampionView(ListAPIView):
    serializer_class = FuelChampionSerializer

    def get_queryset(self):
        queryset = cache.get("FuelChampionQuerySet")
        if queryset is not None:
            return queryset
        round_datetime = RoundCreditStrategy.get_start_of_the_round()
        subquery_user_profile = (
            DonationReceipt.objects.filter(status=ClaimReceipt.VERIFIED)
            .filter(datetime__gt=round_datetime)
            .filter(faucet=OuterRef("faucet"))
            .annotate(float_value=Cast("value", FloatField()))
            .values("user_profile", "faucet")
            .annotate(value=Sum("float_value"))
            .order_by("-value")
            .values("user_profile")[:1]
        )
        username_subquery = UserProfile.objects.filter(
            pk=OuterRef("user_profile")
        ).values("username")
        queryset = (
            DonationReceipt.objects.values("faucet", "user_profile")
            .annotate(max_user_profile=Subquery(subquery_user_profile))
            .filter(max_user_profile__isnull=False)
            .filter(user_profile=F("max_user_profile"))
            .annotate(faucet_pk=F("faucet"))
            .annotate(username=username_subquery)
            .values("faucet_pk", "username")
            .distinct()
        )

        cache.set("FuelChampionQuerySet", queryset, timeout=120)
        return queryset


def artwork_video(request):
    video_file = os.path.join(settings.BASE_DIR, "faucet/artwork.mp4")
    return FileResponse(open(video_file, "rb"), content_type="video/mp4")


def artwork_view(request, token_id):
    # the artwork video file is server under a view called artwork-video
    artwork_video_url = request.build_absolute_uri(reverse("FAUCET:artwork-video"))

    response = {
        "name": "Unitap Pass",
        "description": "Unitap is an onboarding tool for networks \
            and communities and a gateway for users to web3."
        " https://unitap.app . Unitap Pass is a VIP pass for Unitap. Holders"
        " will enjoy various benefits as Unitap grows.",
        "image": artwork_video_url,
        "animation_url": artwork_video_url,
    }

    response_text = json.dumps(response)
    return HttpResponse(response_text, content_type="application/json")


def error500(request):
    1 / 0
