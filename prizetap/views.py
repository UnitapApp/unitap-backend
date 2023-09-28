import json
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from faucet.models import Chain
from faucet.serializers import SmallChainSerializer
from .models import Raffle, RaffleEntry, Constraint
from .serializers import (
    RaffleSerializer, 
    RaffleEntrySerializer,
    ConstraintSerializer,
    CreateRaffleSerializer
)
from .validators import (
    RaffleEnrollmentValidator,
    SetRaffleEntryTxValidator,
    SetClaimingPrizeTxValidator,
    SetRaffleTxValidator
)
from .constraints import *
from .constants import CONTRACT_ADDRESSES


class RaffleListView(ListAPIView):
    queryset = Raffle.objects.filter(is_active=True).order_by("pk")
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

        try:
            raffle_entry = raffle.entries.get(
                user_profile=user_profile
            )
        except RaffleEntry.DoesNotExist:
            raffle_entry = RaffleEntry.objects.create(
                user_profile=user_profile,
                raffle=raffle,
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
    
class SetClaimingPrizeTxView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=pk)
        raffle_entry = get_object_or_404(
            RaffleEntry, raffle=raffle, user_profile=user_profile)

        validator = SetClaimingPrizeTxValidator(
            user_profile=user_profile,
            raffle_entry=raffle_entry
        )
        
        validator.is_valid(self.request.data)

        tx_hash = self.request.data.get("tx_hash", None)
        raffle_entry.claiming_prize_tx = tx_hash
        raffle_entry.save()

        return Response(
            {
                "detail": "Raffle entry updated successfully",
                "success": True,
                "entry": RaffleEntrySerializer(raffle_entry).data
            },
            status=200,
        )

class GetRaffleEntryView(APIView):
    def get(self, request, pk):
        raffle_entry = get_object_or_404(RaffleEntry, pk=pk)

        return Response(
            {
                "success": True,
                "entry": RaffleEntrySerializer(raffle_entry).data
            },
            status=200,
        )

class GetRaffleConstraintsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, raffle_pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=raffle_pk)
        try:
            param_values = json.loads(raffle.constraint_params)
        except:
            param_values = {}

        response_constraints = []

        for c in raffle.constraints.all():
            constraint: ConstraintVerification = eval(c.name)(user_profile)
            constraint.response = c.response
            try:
                constraint.param_values = param_values[c.name]
            except KeyError:
                pass
            is_verified = False
            if constraint.is_observed():
                is_verified = True
            response_constraints.append({
                    **ConstraintSerializer(c).data,
                    "is_verified": is_verified
                })
        
        return Response(
            {
                "success": True,
                "constraints": response_constraints 
            },
            status=200
        )

class CreateRaffleView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateRaffleSerializer

    def post(self, request: Request):
        serializer: CreateRaffleSerializer = self.get_serializer(data=request.data, context={
            'user_profile': request.user.profile
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            "data": serializer.data
        })


class SetRaffleTXView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_profile = request.user.profile
        raffle = get_object_or_404(Raffle, pk=pk)

        validator = SetRaffleTxValidator(
            user_profile=user_profile,
            raffle=raffle
        )
        
        validator.is_valid(self.request.data)
        
        tx_hash = self.request.data.get("tx_hash", None)
        raffle.tx_hash = tx_hash
        raffle.save()

        return Response(
            {
                "detail": "Raffle updated successfully",
                "success": True,
                "raffle": RaffleSerializer(raffle, context={
                    'user': request.user.profile
                }).data
            },
            status=200,
        )

class ValidChainsView(ListAPIView):
    queryset = Chain.objects.filter(chain_id__in=list(CONTRACT_ADDRESSES.keys()))
    serializer_class = SmallChainSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = SmallChainSerializer(queryset, many=True)
        response = []
        for chain in serializer.data:
            response.append({
                **chain,
                **CONTRACT_ADDRESSES[chain['chain_id']]
            })
        return Response({
            "success": True,
            "data": response
        })

class UserRafflesListView(ListAPIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        queryset = Raffle.objects.filter(creator_profile=request.user.profile).order_by("pk")
        serializer = RaffleSerializer(queryset, many=True, context={
            'user': request.user.profile
        })
        return Response(serializer.data)

class ConstraintsListView(ListAPIView):
    queryset = Constraint.objects.all()
    serializer_class = ConstraintSerializer

