import datetime
import json
import logging
import os

import pytz
import rest_framework.exceptions
from django.conf import settings
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import FloatField, OuterRef, Subquery, Sum
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

from authentication.models import UserProfile, Wallet
from core.filters import ChainFilterBackend, IsOwnerFilterBackend
from core.paginations import StandardResultsSetPagination
from faucet.faucet_manager.claim_manager import (
    ClaimManagerFactory,
    LimitedChainClaimManager,
)
from faucet.faucet_manager.credit_strategy import RoundCreditStrategy
from faucet.models import Chain, ClaimReceipt, DonationReceipt, GlobalSettings
from faucet.serializers import (
    ChainBalanceSerializer,
    ChainSerializer,
    DonationReceiptSerializer,
    GlobalSettingsSerializer,
    LeaderboardSerializer,
    ReceiptSerializer,
    SmallChainSerializer,
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
            return ClaimReceipt.objects.filter(user_profile=user_profile).order_by("pk").last()
        except ClaimReceipt.DoesNotExist:
            raise Http404("Claim Receipt for this user does not exist")


class ListClaims(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptSerializer

    filterset_fields = {
        "chain": {"exact"},
        "_status": {"exact"},
        "datetime": {"exact", "gte", "lte"},
    }

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
            chain__in=Chain.objects.filter(is_one_time_claim=True),
            _status__in=[
                ClaimReceipt.VERIFIED,
                ClaimReceipt.PENDING,
                ClaimReceipt.REJECTED,
            ],
            # 1 November 2023
            datetime__lt=datetime.datetime(
                2023, 11, 1, 0, 0, 0, 0, pytz.timezone("UTC")
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
            result = max(gs.gastap_round_claim_limit - LimitedChainClaimManager.get_total_round_claims(user_profile), 0)
            return Response({"total_round_claims_remaining": result}, status=200)
        else:
            raise Http404("Global Settings Not Found")


class ChainListView(ListAPIView):
    """
    list of supported chains

    this endpoint returns detailed user specific info if supplied with an address
    """

    serializer_class = ChainSerializer

    def get_queryset(self):
        queryset = Chain.objects.filter(is_active=True, show_in_gastap=True)

        sorted_queryset = sorted(queryset, key=lambda obj: obj.total_claims_since_last_round, reverse=True)
        return sorted_queryset


class SmallChainListView(ListAPIView):
    """
    list of supported chains with minimum details

    """

    serializer_class = SmallChainSerializer
    queryset = Chain.objects.filter(is_active=True)


class GlobalSettingsView(RetrieveAPIView):
    serializer_class = GlobalSettingsSerializer

    def get_object(self):
        return GlobalSettings.objects.first()


class ClaimMaxView(APIView):
    """
    Claims maximum possible fee for the given user and chain

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
            raise CustomException("You are not BrighID verified")

    def wallet_address_is_set(self):
        passive_address = self.request.data.get("address", None)
        if passive_address is not None:
            return True, passive_address

        chain = self.get_chain()

        try:
            Wallet.objects.get(user_profile=self.get_user(), wallet_type=chain.chain_type)
            return True, None
        except Exception as e:
            logging.error("wallet address not set", e)
            raise CustomException("wallet address not set")

    def get_chain(self) -> Chain:
        chain_pk = self.kwargs.get("chain_pk", None)
        try:
            return Chain.objects.get(pk=chain_pk)
        except Chain.DoesNotExist:
            raise Http404(f"Chain with id {chain_pk} Does not Exist")

    def get_claim_manager(self):
        return ClaimManagerFactory(self.get_chain(), self.get_user()).get_manager()

    def claim_max(self, passive_address) -> ClaimReceipt:
        manager = self.get_claim_manager()
        max_credit = manager.get_credit_strategy().get_unclaimed()
        try:
            assert max_credit > 0
            return manager.claim(max_credit, passive_address=passive_address)
        except AssertionError as e:
            logging.error("no credit left for user", e)
            raise CustomException("no credit left")
        except ValueError as e:
            raise rest_framework.exceptions.APIException(e)

    def post(self, request, *args, **kwargs):
        try:
            self.check_user_is_verified()
            s, passive_address = self.wallet_address_is_set()
        except CustomException as e:
            return Response({"message": str(e)}, status=403)

        receipt = self.claim_max(passive_address)
        return Response(ReceiptSerializer(instance=receipt).data)


class ChainBalanceView(RetrieveAPIView):
    serializer_class = ChainBalanceSerializer

    def get_object(self):
        chain_pk = self.kwargs.get("chain_pk", None)
        if chain_pk is None:
            raise Http404("Chain ID not provided")
        return Chain.objects.get(pk=chain_pk)


class DonationReceiptView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DonationReceiptSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [IsOwnerFilterBackend, ChainFilterBackend]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.get_user()})
        return context

    def get_queryset(self):
        return DonationReceipt.objects.all()

    def get_user(self) -> UserProfile:
        return self.request.user.profile


class UserLeaderboardView(RetrieveAPIView):
    filter_backends = [ChainFilterBackend]
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
        user_rank = queryset.filter(sum_total_price__gt=user_obj.get("sum_total_price")).count() + 1
        user_obj["rank"] = user_rank
        user_obj["username"] = self.get_user().username
        user_obj["wallet"] = self.get_user().wallets.all()[0].address
        interacted_chains = list(
            DonationReceipt.objects.filter(user_profile=self.get_user())
            .filter(status=ClaimReceipt.VERIFIED)
            .values_list("chain", flat=True)
            .distinct()
        )
        user_obj["interacted_chains"] = interacted_chains

        return user_obj


class LeaderboardView(ListAPIView):
    serializer_class = LeaderboardSerializer
    pagination_class = StandardResultsSetPagination
    queryset = DonationReceipt.objects.all()
    filter_backends = [ChainFilterBackend]

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
            .values_list("chain", flat=True)
            .distinct()
        )
        queryset = donation_receipt.annotate(interacted_chains=ArraySubquery(subquery_interacted_chains))
        subquery_username = UserProfile.objects.filter(pk=OuterRef("user_profile")).values("username")
        subquery_wallet = Wallet.objects.filter(user_profile=OuterRef("user_profile")).values("address")
        queryset = queryset.annotate(username=Subquery(subquery_username), wallet=Subquery(subquery_wallet))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def artwork_video(request):
    video_file = os.path.join(settings.BASE_DIR, "faucet/artwork.mp4")
    return FileResponse(open(video_file, "rb"), content_type="video/mp4")


def artwork_view(request, token_id):
    # the artwork video file is server under a view called artwork-video
    artwork_video_url = request.build_absolute_uri(reverse("FAUCET:artwork-video"))

    response = {
        "name": "Unitap Pass",
        "description": "Unitap is an onboarding tool for networks and communities and a gateway for users to web3."
        " https://unitap.app . Unitap Pass is a VIP pass for Unitap. Holders"
        " will enjoy various benefits as Unitap grows.",
        "image": artwork_video_url,
        "animation_url": artwork_video_url,
    }

    response_text = json.dumps(response)
    return HttpResponse(response_text, content_type="application/json")


def error500(request):
    1 / 0
