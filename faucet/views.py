import json
import logging
from django.http import FileResponse
import os
import rest_framework.exceptions
from django.http import Http404
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from authentication.models import UserProfile, Wallet
from faucet.faucet_manager.claim_manager import (
    ClaimManagerFactory,
    LimitedChainClaimManager,
)
from faucet.faucet_manager.claim_manager import WeeklyCreditStrategy
from faucet.models import Chain, ClaimReceipt, GlobalSettings
from faucet.serializers import (
    GlobalSettingsSerializer,
    ReceiptSerializer,
    ChainSerializer,
)

# import BASE_DIR from django settings
from django.conf import settings


class CustomException(Exception):
    pass


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

    filterset_fields = {
        "chain": {"exact"},
        "_status": {"exact"},
        "datetime": {"exact", "gte", "lte"},
    }

    def get_queryset(self):
        user_profile = self.request.user.profile
        return ClaimReceipt.objects.filter(
            user_profile=user_profile,
            datetime__gte=WeeklyCreditStrategy.get_last_monday(),
        ).order_by("-pk")


class GetTotalWeeklyClaimsRemainingView(RetrieveAPIView):
    """
    Return the total weekly claims remaining for the given user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        gs = GlobalSettings.objects.first()
        if gs is not None:
            result = (
                gs.weekly_chain_claim_limit
                - LimitedChainClaimManager.get_total_weekly_claims(user_profile)
            )
            return Response({"total_weekly_claims_remaining": result}, status=200)
        else:
            raise Http404("Global Settings Not Found")


class ChainListView(ListAPIView):
    """
    list of supported chains

    this endpoint returns detailed user specific info if supplied with an address
    """

    serializer_class = ChainSerializer

    def get_queryset(self):
        queryset = Chain.objects.filter(is_active=True).prefetch_related("claims")

        sorted_queryset = sorted(
            queryset, key=lambda obj: obj.total_claims_since_last_round, reverse=True
        )
        return sorted_queryset


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
            _wallet = Wallet.objects.get(
                user_profile=self.get_user(), wallet_type=chain.chain_type
            )
            return True, None
        except Exception as e:
            raise CustomException("wallet address not set")
            # return Response({"message": "wallet address not set"}, status=403)

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
            # return Response({"message": "no credit left"}, status=403)
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


def artwork_video(request):
    video_file = os.path.join(settings.BASE_DIR, f"faucet/artwork.mp4")
    return FileResponse(open(video_file, "rb"), content_type="video/mp4")


def artwork_view(request, token_id):
    # the artwork video file is server under a view called artwork-video
    artwork_video_url = request.build_absolute_uri(reverse("FAUCET:artwork-video"))

    response = {
        "name": "Unitap Pass",
        "description": "Unitap is an onboarding tool for networks and communities and a gateway for users to web3. https://unitap.app . Unitap Pass is a VIP pass for Unitap. Holders will enjoy various benefits as Unitap grows.",
        "image": artwork_video_url,
        "animation_url": artwork_video_url,
    }

    response_text = json.dumps(response)
    return HttpResponse(response_text, content_type="application/json")


def error500(request):
    1 / 0
