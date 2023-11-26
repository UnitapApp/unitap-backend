import json
import logging

import rest_framework.exceptions
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import NetworkTypes
from core.constraints import ConstraintVerification, get_constraint
from faucet.models import ClaimReceipt
from tokenTap.models import TokenDistribution, TokenDistributionClaim
from tokenTap.serializers import (
    ConstraintSerializer,
    DetailResponseSerializer,
    TokenDistributionClaimResponseSerializer,
    TokenDistributionClaimSerializer,
    TokenDistributionSerializer,
)

from .helpers import (
    create_uint32_random_nonce,
    has_weekly_credit_left,
    hash_message,
    sign_hashed_message,
)


class TokenDistributionListView(ListAPIView):
    serializer_class = TokenDistributionSerializer
    queryset = TokenDistribution.objects.filter(is_active=True)

    def get_queryset(self):
        q = TokenDistribution.objects.filter(is_active=True)

        sorted_queryset = sorted(q, key=lambda obj: obj.total_claims_since_last_round, reverse=True)

        return sorted_queryset


class TokenDistributionClaimView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def check_token_distribution_is_claimable(self, token_distribution):
        if not token_distribution.is_claimable:
            raise rest_framework.exceptions.PermissionDenied("This token is not claimable")

    def check_user_permissions(self, token_distribution, user_profile):
        for c in token_distribution.permissions.all():
            constraint: ConstraintVerification = get_constraint(c.name)(user_profile)
            constraint.response = c.response
            if not constraint.is_observed(token_distribution=token_distribution):
                raise PermissionDenied(constraint.response)

    def check_user_weekly_credit(self, user_profile):
        if not has_weekly_credit_left(user_profile):
            raise rest_framework.exceptions.PermissionDenied("You have reached your weekly claim limit")

    def check_user_has_wallet(self, user_profile):
        if not user_profile.wallets.filter(wallet_type=NetworkTypes.EVM).exists():
            raise rest_framework.exceptions.PermissionDenied("You have not connected an EVM wallet to your account")

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
        lightning_invoice = request.data.get("lightning_invoice", None)

        self.check_token_distribution_is_claimable(token_distribution)

        self.check_user_has_wallet(user_profile)

        self.check_user_permissions(token_distribution, user_profile)

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

        self.check_user_weekly_credit(user_profile)

        nonce = create_uint32_random_nonce()
        if token_distribution.chain.chain_type == NetworkTypes.EVM:
            hashed_message = hash_message(
                user=user_profile.wallets.get(wallet_type=NetworkTypes.EVM).address,
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
            )

        elif token_distribution.chain.chain_type == NetworkTypes.LIGHTNING:
            tdc = TokenDistributionClaim.objects.create(
                user_profile=user_profile,
                nonce=nonce,
                signature=lightning_invoice,
                token_distribution=token_distribution,
            )
            ClaimReceipt.objects.create(
                chain=token_distribution.chain,
                user_profile=user_profile,
                datetime=timezone.now(),
                amount=token_distribution.amount,
                _status=ClaimReceipt.PENDING,
                passive_address=lightning_invoice,
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

        response_constraints = []

        for c in td.permissions.all():
            constraint: ConstraintVerification = get_constraint(c.name)(user_profile)
            constraint.response = c.response
            try:
                constraint.param_values = param_values[c.name]
            except KeyError:
                pass
            is_verified = False
            if constraint.is_observed(token_distribution=td):
                is_verified = True
            response_constraints.append({**ConstraintSerializer(c).data, "is_verified": is_verified})

        return Response({"success": True, "constraints": response_constraints}, status=200)


class TokenDistributionClaimStatusUpdateView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_profile = request.user.profile
        token_distribution_claim = TokenDistributionClaim.objects.get(
            pk=self.kwargs["pk"],
        )
        tx_hash = request.data.get("tx_hash", None)
        if tx_hash is None:
            raise rest_framework.exceptions.ValidationError("tx_hash is a required field")

        if token_distribution_claim.user_profile != user_profile:
            raise rest_framework.exceptions.PermissionDenied("You do not have permission to update this claim")
        if token_distribution_claim.status != ClaimReceipt.PENDING:
            raise rest_framework.exceptions.PermissionDenied("This claim has already been updated")
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
        return TokenDistributionClaim.objects.get(pk=self.kwargs["pk"], user_profile=user_profile)
