from django.shortcuts import get_object_or_404
import rest_framework.exceptions
from rest_framework.response import Response
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from authentication.models import NetworkTypes, UserProfile
from .models import Raffle, RaffleEntry
from .serializers import RaffleSerializer, RaffleEntrySerializer
from .validators import (
    RaffleEnrollmentValidator,
    SetRaffleEntryTxValidator
)

from permissions.models import Permission


class RaffleListView(ListAPIView):
    queryset = Raffle.objects.filter(is_active=True)
    serializer_class = RaffleSerializer

class RaffleEnrollmentView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=pk)
        
        validator = RaffleEnrollmentValidator(
            user_profile=user_profile,
            raffle=raffle
        )
        
        validator.is_valid(self.request.data)

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
    
class SetEnrollmentTxView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle_entry = get_object_or_404(RaffleEntry, pk=pk)

        validator = SetRaffleEntryTxValidator(
            user_profile=user_profile,
            raffle_entry=raffle_entry
        )
        
        validator.is_valid(self.request.data)
        
        tx_hash = self.request.data.get("tx_hash", None)
        raffle_entry.tx_hash = tx_hash
        raffle_entry.save()

        return Response(
            {
                "detail": "Raffle entry updated successfully",
                "success": True,
                "entry": RaffleEntrySerializer(raffle_entry).data
            },
            status=200,
        )
