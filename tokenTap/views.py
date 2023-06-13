import rest_framework.exceptions
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from authentication.models import NetworkTypes, UserProfile, Wallet
from authentication.serializers import MessageResponseSerializer
from faucet.models import Chain, GlobalSettings
from permissions.models import Permission
from tokenTap.models import TokenDistribution, TokenDistributionClaim
from tokenTap.serializers import (
    DetailResponseSerializer,
    TokenDistributionClaimResponseSerializer,
    TokenDistributionClaimSerializer,
    TokenDistributionSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .helpers import (
    create_uint32_random_nonce,
    hash_message,
    sign_hashed_message,
    has_weekly_credit_left,
)


class TokenDistributionListView(ListAPIView):
    serializer_class = TokenDistributionSerializer
    queryset = TokenDistribution.objects.filter(is_active=True)


class TokenDistributionClaimView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def check_token_distribution_is_claimable(self, token_distribution):
        if not token_distribution.is_claimable:
            raise rest_framework.exceptions.PermissionDenied(
                "This token is not claimable"
            )

    def check_user_permissions(self, token_distribution, user_profile):
        for permission in token_distribution.permissions.all():
            permission: Permission
            if not permission.is_valid(
                user_profile, token_distribution=token_distribution
            ):
                raise rest_framework.exceptions.PermissionDenied(
                    permission.response()
                    if permission.response() is not None
                    else "You do not have permission to claim this token"
                )

    def check_user_weekly_credit(self, user_profile):
        if not has_weekly_credit_left(user_profile):
            raise rest_framework.exceptions.PermissionDenied(
                "You have reached your weekly claim limit"
            )

    def check_user_has_wallet(self, user_profile):
        if not user_profile.wallets.filter(wallet_type=NetworkTypes.EVM).exists():
            raise rest_framework.exceptions.PermissionDenied(
                "You have not connected an EVM wallet to your account"
            )

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

        self.check_token_distribution_is_claimable(token_distribution)

        self.check_user_weekly_credit(user_profile)

        self.check_user_permissions(token_distribution, user_profile)

        self.check_user_has_wallet(user_profile)

        nonce = create_uint32_random_nonce()
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

        return Response(
            {
                "detail": "Signature Created Successfully",
                "signature": TokenDistributionClaimSerializer(tdc).data,
            },
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
