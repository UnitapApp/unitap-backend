import json
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
from authentication.models import UserProfile
from faucet.faucet_manager.claim_manager import (
    ClaimManagerFactory,
    LimitedChainClaimManager,
)
from faucet.models import Chain, ClaimReceipt, GlobalSettings
from faucet.serializers import (
    GlobalSettingsSerializer,
    ReceiptSerializer,
    ChainSerializer,
)

# import BASE_DIR from django settings
from django.conf import settings


# class CreateUserView(CreateAPIView):
#     """
#     Create an unverified user with the given address

#     this user can be verified using verification_link
#     """

#     serializer_class = UserSerializer


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
        return ClaimReceipt.objects.filter(user_profile=user_profile).order_by("-pk")


# class UserInfoView(RetrieveAPIView):
#     """
#     User info of the given address
#     """

#     serializer_class = UserSerializer
#     queryset = BrightUser.objects.all()

#     lookup_field = "address"
#     lookup_url_kwarg = "address"


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


# class GetVerificationUrlView(RetrieveAPIView):
#     """
#     Return the bright verification url
#     """

#     serializer_class = UserSerializer

#     def get_object(self):
#         address = self.kwargs.get("address")
#         try:
#             return BrightUser.objects.get(address=address)
#         except BrightUser.DoesNotExist:
#             if address is not None:
#                 return BrightUser.objects.get_or_create(address)

#             raise Http404


class ChainListView(ListAPIView):
    """
    list of supported chains

    this endpoint returns detailed user specific info if supplied with an address
    """

    serializer_class = ChainSerializer
    queryset = Chain.objects.filter(is_active=True).order_by("order")


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
        if not _is_verified:
            raise rest_framework.exceptions.NotAcceptable

    def wallet_address_is_set(self):
        _wallets = self.get_user().wallets
        _address = self.request.data.get("address", None)
        if not _wallets.exists() and _address is None:
            print("No Wallets and No Address")
            raise rest_framework.exceptions.NotAcceptable
        if self.get_chain().chain_type == "NONEVM" and _address is None:
            print("No NONEVM Address")
            raise rest_framework.exceptions.NotAcceptable
        return True

    def get_chain(self) -> Chain:
        chain_pk = self.kwargs.get("chain_pk", None)
        try:
            return Chain.objects.get(pk=chain_pk)
        except Chain.DoesNotExist:
            raise Http404(f"Chain with id {chain_pk} Does not Exist")

    def get_claim_manager(self):
        return ClaimManagerFactory(self.get_chain(), self.get_user()).get_manager()

    def claim_max(self) -> ClaimReceipt:
        manager = self.get_claim_manager()
        max_credit = manager.get_credit_strategy().get_unclaimed()
        try:
            assert max_credit > 0
            return manager.claim(max_credit)
        except AssertionError as e:
            raise rest_framework.exceptions.PermissionDenied
        except ValueError as e:
            raise rest_framework.exceptions.APIException(e)

    def post(self, request, *args, **kwargs):
        self.check_user_is_verified()
        receipt = self.claim_max()
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
