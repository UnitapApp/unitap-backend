from django.shortcuts import get_object_or_404
import rest_framework.exceptions
from rest_framework.response import Response
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from authentication.models import NetworkTypes, UserProfile
from .models import Raffle, RaffleEntry
from .serializers import RaffleSerializer, RaffleEntrySerializer
from .utils import create_uint32_random_nonce
from .validators import has_weekly_credit_left

from permissions.models import Permission


class RaffleListView(ListAPIView):
    queryset = Raffle.objects.filter(is_active=True)
    serializer_class = RaffleSerializer

class RaffleEnrollmentView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def can_enroll_in_raffle(self, raffle: Raffle):
        if not raffle.is_claimable:
            raise rest_framework.exceptions.PermissionDenied(
                "Can't enroll in this raffle"
            )
        
    def check_user_is_already_enrolled(
            self, raffle: Raffle, user_profile: UserProfile
        ):
        if RaffleEntry.objects.filter(
            raffle=raffle,
            user_profile=user_profile
        ).exists():
            raise rest_framework.exceptions.PermissionDenied(
                "You're already enrolled in this raffle"
            )
        
    def check_user_permissions(self, raffle: Raffle, user_profile):
        for permission in raffle.permissions.all():
            permission: Permission
            if not permission.is_valid(
                user_profile, raffle=raffle
            ):
                raise rest_framework.exceptions.PermissionDenied(
                    permission.response()
                    if permission.response() is not None
                    else "You do not have permission to enroll in this raffle"
                )

    def check_user_weekly_credit(self, user_profile):
        if not has_weekly_credit_left(user_profile):
            raise rest_framework.exceptions.PermissionDenied(
                "You have reached your weekly enrollment limit"
            )

    def check_user_has_wallet(self, user_profile):
        if not user_profile.wallets.filter(wallet_type=NetworkTypes.EVM).exists():
            raise rest_framework.exceptions.PermissionDenied(
                "You have not connected an EVM wallet to your account"
            )

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=pk)
        
        self.can_enroll_in_raffle(raffle)

        self.check_user_is_already_enrolled(raffle, user_profile)

        self.check_user_weekly_credit(user_profile)

        self.check_user_permissions(raffle, user_profile)

        self.check_user_has_wallet(user_profile)

        raffle_entry = RaffleEntry.objects.create(
            user_profile=user_profile,
            raffle=raffle,
        )
        raffle_entry.signature = raffle.generate_signature(
            user_profile.wallets.get(wallet_type=NetworkTypes.EVM).address, raffle_entry.pk
        )
        raffle_entry.save()

        return Response(
            {
                "detail": "Signature Created Successfully",
                "signature": RaffleEntrySerializer(raffle_entry).data,
            },
            status=200,
        )

class ClaimPrizeView(APIView):
    permission_classes = [IsAuthenticated]

    def can_claim_prize(self, raffle: Raffle, user_profile: UserProfile):
        if not raffle.is_expired:
            raise rest_framework.exceptions.PermissionDenied(
                "The raffle is not over"
            )
        if not raffle.winner or raffle.winner != user_profile:
            raise rest_framework.exceptions.PermissionDenied(
                "You are not the raffle winner"
            )
        
    def check_user_permissions(self, raffle: Raffle, user_profile):
        for permission in raffle.permissions.all():
            permission: Permission
            if not permission.is_valid(
                user_profile, raffle=raffle
            ):
                raise rest_framework.exceptions.PermissionDenied(
                    permission.response()
                    if permission.response() is not None
                    else "You do not have permission to enroll in this raffle"
                )

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=pk)
        
        self.can_claim_prize(raffle, user_profile)

        self.check_user_permissions(raffle, user_profile)

        signature = raffle.generate_signature(
            user_profile.wallets.get(wallet_type=NetworkTypes.EVM).address)

        return Response(
            {
                "detail": "Signature created successfully",
                "success": True,
                "signature": signature
            },
            status=200,
        )
