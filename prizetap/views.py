from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from authentication.models import NetworkTypes
from .models import Raffle, RaffleEntry
from .serializers import RaffleSerializer, RaffleEntrySerializer
from .validators import (
    RaffleEnrollmentValidator,
    ClaimPrizeValidator,
    SetRaffleEntryTxValidator
)

from permissions.models import Permission


class RaffleListView(ListAPIView):
    queryset = Raffle.objects.filter(is_active=True)
    serializer_class = RaffleSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = RaffleSerializer(queryset, many=True, context={
            'user': request.user.profile if request.user.is_authenticated else None
        })
        return Response(serializer.data)

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

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=pk)
        
        validator = ClaimPrizeValidator(
            user_profile=user_profile,
            raffle=raffle
        )
        
        validator.is_valid(self.request.data)

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
