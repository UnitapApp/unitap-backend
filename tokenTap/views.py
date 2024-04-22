import json
import logging

import rest_framework.exceptions
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.constraints import ConstraintVerification, get_constraint
from core.models import Chain, NetworkTypes
from core.serializers import ChainSerializer
from core.swagger import ConstraintProviderSrializerInspector
from core.views import AbstractConstraintsListView
from faucet.models import ClaimReceipt, Faucet
from tokenTap.models import Constraint, TokenDistribution, TokenDistributionClaim
from tokenTap.serializers import (
    ConstraintSerializer,
    CreateTokenDistributionSerializer,
    DetailResponseSerializer,
    TokenDistributionClaimResponseSerializer,
    TokenDistributionClaimSerializer,
    TokenDistributionSerializer,
)

from .constants import CONTRACT_ADDRESSES
from .helpers import (
    create_uint32_random_nonce,
    has_credit_left,
    hash_message,
    sign_hashed_message,
)
from .validators import SetDistributionTxValidator


class TokenDistributionListView(ListAPIView):
    serializer_class = TokenDistributionSerializer
    queryset = TokenDistribution.objects.filter(is_active=True)

    def get_queryset(self):
        q = TokenDistribution.objects.filter(is_active=True)

        sorted_queryset = sorted(
            q, key=lambda obj: obj.total_claims_since_last_round, reverse=True
        )

        return sorted_queryset


class TokenDistributionClaimView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def check_token_distribution_is_claimable(self, token_distribution):
        if not token_distribution.is_claimable:
            raise rest_framework.exceptions.PermissionDenied(
                "This token is not claimable"
            )

    def check_user_permissions(self, token_distribution, user_profile):
        try:
            param_values = json.loads(token_distribution.constraint_params)
        except Exception:
            param_values = {}
        for c in token_distribution.constraints.all():
            constraint: ConstraintVerification = get_constraint(c.name)(user_profile)
            constraint.response = c.response
            try:
                constraint.param_values = param_values[c.name]
            except KeyError:
                pass
            if str(c.pk) in token_distribution.reversed_constraints_list:
                if constraint.is_observed(token_distribution=token_distribution):
                    raise PermissionDenied(constraint.response)
            else:
                if not constraint.is_observed(token_distribution=token_distribution):
                    raise PermissionDenied(constraint.response)

    def check_user_credit(self, distribution, user_profile):
        if distribution.is_one_time_claim:
            already_claimed = distribution.claims.filter(
                user_profile=user_profile,
                status=ClaimReceipt.VERIFIED,
            ).exists()
            if already_claimed:
                raise rest_framework.exceptions.PermissionDenied(
                    "You have already claimed"
                )
        elif not has_credit_left(distribution, user_profile):
            raise rest_framework.exceptions.PermissionDenied(
                "You have reached your claim limit"
            )

    def wallet_is_vaild(self, user_profile, user_wallet_address, token_distribution):
        if token_distribution.chain.chain_type == NetworkTypes.LIGHTNING:
            return  # TODO - check if user_wallet_address is a valid lightning invoice

        elif token_distribution.chain.chain_type == NetworkTypes.EVM:
            if not user_profile.owns_wallet(user_wallet_address):
                raise PermissionDenied("This wallet is not registered for this user")

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Signature Created Successfully",
                schema=TokenDistributionClaimResponseSerializer(),
            ),
            403: openapi.Response(
                description="This token is not claimable"
                + " | "
                + "You have reached your weekly claim limit"
                + " | "
                + "You do not have permission to claim this token"
                + " | "
                + "You have not connected an EVM wallet to your account"
                + " | "
                + "You have already claimed this token this week"
                + " | "
                + "You have already claimed this token this month",
                schema=DetailResponseSerializer(),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        user_profile = request.user.profile
        token_distribution = TokenDistribution.objects.get(pk=self.kwargs["pk"])
        user_wallet_address = request.data.get("user_wallet_address", None)
        if user_wallet_address is None:
            raise rest_framework.exceptions.ParseError(
                "user_wallet_address is a required field"
            )

        self.wallet_is_vaild(user_profile, user_wallet_address, token_distribution)

        try:
            tdc = TokenDistributionClaim.objects.get(
                user_profile=user_profile,
                token_distribution=token_distribution,
                status=ClaimReceipt.PENDING,
            )
            return Response(
                {
                    "detail": "Signature Was Already Created",
                    "signature": TokenDistributionClaimSerializer(tdc).data,
                },
                status=200,
            )

        except TokenDistributionClaim.DoesNotExist:
            pass

        self.check_user_permissions(token_distribution, user_profile)

        self.check_token_distribution_is_claimable(token_distribution)

        self.check_user_credit(token_distribution, user_profile)

        nonce = create_uint32_random_nonce()
        if token_distribution.chain.chain_type == NetworkTypes.EVM:
            hashed_message = hash_message(
                address=user_wallet_address,
                token=token_distribution.token_address,
                amount=token_distribution.amount,
                nonce=nonce,
            )

            signature = sign_hashed_message(hashed_message=hashed_message)

            tdc = TokenDistributionClaim.objects.create(
                user_profile=user_profile,
                nonce=nonce,
                signature=signature,
                token_distribution=token_distribution,
                user_wallet_address=user_wallet_address,
            )

        elif token_distribution.chain.chain_type == NetworkTypes.LIGHTNING:
            tdc = TokenDistributionClaim.objects.create(
                user_profile=user_profile,
                nonce=nonce,
                signature=user_wallet_address,
                user_wallet_address=user_wallet_address,
                token_distribution=token_distribution,
            )
            ClaimReceipt.objects.create(
                faucet=Faucet.objects.get(chain__chain_type=NetworkTypes.LIGHTNING),
                user_profile=user_profile,
                datetime=timezone.now(),
                amount=token_distribution.amount,
                _status=ClaimReceipt.PENDING,
                to_address=user_wallet_address,
            )

        return Response(
            {
                "detail": "Signature Created Successfully",
                "signature": TokenDistributionClaimSerializer(tdc).data,
            },
            status=200,
        )


class GetTokenDistributionConstraintsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, td_id):
        user_profile = request.user.profile
        td = get_object_or_404(TokenDistribution, pk=td_id)
        try:
            param_values = json.loads(td.constraint_params)
        except Exception as e:
            logging.error("Error parsing constraint params", e)
            param_values = {}

        reversed_constraints = td.reversed_constraints_list
        response_constraints = []

        for c in td.constraints.all():
            constraint: ConstraintVerification = get_constraint(c.name)(user_profile)
            constraint.response = c.response
            try:
                constraint.param_values = param_values[c.name]
            except KeyError:
                pass
            is_verified = False
            if str(c.pk) in reversed_constraints:
                if not constraint.is_observed(token_distribution=td):
                    is_verified = True
            else:
                if constraint.is_observed(token_distribution=td):
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


class TokenDistributionClaimStatusUpdateView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_profile = request.user.profile
        token_distribution_claim = TokenDistributionClaim.objects.get(
            pk=self.kwargs["pk"],
        )
        tx_hash = request.data.get("tx_hash", None)
        if tx_hash is None:
            raise rest_framework.exceptions.ValidationError(
                "tx_hash is a required field"
            )

        if token_distribution_claim.user_profile != user_profile:
            raise rest_framework.exceptions.PermissionDenied(
                "You do not have permission to update this claim"
            )
        if token_distribution_claim.status != ClaimReceipt.PENDING:
            raise rest_framework.exceptions.PermissionDenied(
                "This claim has already been updated"
            )
        token_distribution_claim.tx_hash = tx_hash
        token_distribution_claim.status = ClaimReceipt.VERIFIED
        token_distribution_claim.save()

        return Response(
            {"detail": "Token Distribution Claim Status Updated Successfully"},
            status=200,
        )


class TokenDistributionClaimListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TokenDistributionClaimSerializer

    def get_queryset(self):
        user_profile = self.request.user.profile
        return TokenDistributionClaim.objects.filter(user_profile=user_profile)


class TokenDistributionClaimRetrieveView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TokenDistributionClaimSerializer

    def get_object(self):
        user_profile = self.request.user.profile
        return TokenDistributionClaim.objects.get(
            pk=self.kwargs["pk"], user_profile=user_profile
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
            response.append(
                {
                    **chain,
                    "tokentap_contract_address": CONTRACT_ADDRESSES[chain["chain_id"]],
                }
            )
        return Response({"success": True, "data": response})


class CreateTokenDistribution(CreateAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [IsAuthenticated]
    serializer_class = CreateTokenDistributionSerializer

    @swagger_auto_schema(field_inspectors=[ConstraintProviderSrializerInspector])
    def post(self, request: Request):
        serializer: CreateTokenDistributionSerializer = self.get_serializer(
            data=request.data, context={"user_profile": request.user.profile}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data})


class UserTokenDistributionsView(ListAPIView):
    serializer_class = TokenDistributionSerializer
    queryset = TokenDistribution.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TokenDistribution.objects.filter(
            is_active=True, distributor_profile=self.request.user.profile
        ).order_by("-pk")


class ConstraintsListView(AbstractConstraintsListView):
    queryset = Constraint.objects.filter(is_active=True)
    serializer_class = ConstraintSerializer


class ClaimDetailView(APIView):
    def get(self, request, pk):
        claim = get_object_or_404(TokenDistributionClaim, pk=pk)

        return Response(
            {"success": True, "data": TokenDistributionClaimSerializer(claim).data},
            status=200,
        )


class SetDistributionTXView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_profile = request.user.profile
        token_distribution = get_object_or_404(TokenDistribution, pk=pk)

        validator = SetDistributionTxValidator(
            user_profile=user_profile, token_distribution=token_distribution
        )

        validator.is_valid(self.request.data)

        tx_hash = self.request.data.get("tx_hash", None)
        token_distribution.tx_hash = tx_hash
        token_distribution.save()

        return Response(
            {
                "detail": "Token distribution updated successfully",
                "success": True,
                "token_distribution": TokenDistributionSerializer(
                    token_distribution, context={"user": request.user.profile}
                ).data,
            },
            status=200,
        )
