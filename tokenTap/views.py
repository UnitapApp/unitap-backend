import rest_framework.exceptions
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import UserProfile
from core.models import Chain, NetworkTypes
from core.serializers import ChainSerializer
from core.swagger import ConstraintProviderSrializerInspector
from core.views import AbstractConstraintsListView
from faucet.models import ClaimReceipt
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
from .helpers import create_uint32_random_nonce, hash_message, sign_hashed_message
from .validators import SetDistributionTxValidator, TokenDistributionValidator


class TokenDistributionListView(ListAPIView):
    serializer_class = TokenDistributionSerializer
    queryset = TokenDistribution.objects.filter(is_active=True)

    def get_queryset(self):
        q = TokenDistribution.objects.filter(is_active=True).order_by("-pk")

        sorted_queryset = sorted(q, key=lambda obj: obj.is_expired, reverse=False)

        return sorted_queryset


class TokenDistributionClaimView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def wallet_is_valid(self, user_profile, user_wallet_address, token_distribution):
        if token_distribution.chain.chain_type == NetworkTypes.EVM:
            if not user_profile.owns_wallet(user_wallet_address):
                raise PermissionDenied("This wallet is not registered for this user")

    def check_unitap_pass_share(
        self, distribution: TokenDistribution, user_profile: UserProfile
    ) -> tuple[bool, list[int]]:
        if (
            distribution.remaining_claim_for_unitap_pass_user is None
            or not distribution.remaining_claim_for_unitap_pass_user > 0
        ):
            return False, list()

        has_unitap_pass, unitap_pass_list = user_profile.has_unitap_pass()
        if has_unitap_pass:
            used_unitap_passes = set(distribution.used_unitap_pass_list)
            not_used_unitap_passes = set(unitap_pass_list) - used_unitap_passes
            if not len(not_used_unitap_passes):
                raise PermissionDenied("You use all your unitap passes")
            return has_unitap_pass, list(not_used_unitap_passes)

        if distribution.claims.filter(is_unitap_pass_share=False).count() >= (
            distribution.max_number_of_claims
            - distribution.max_claim_number_for_unitap_pass_user
        ):
            raise PermissionDenied("Only unitap pass user could claim.")

        return False, list()

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
        with transaction.atomic():
            user_profile = request.user.profile
            token_distribution = TokenDistribution.objects.select_for_update().get(
                pk=self.kwargs["pk"]
            )
            td_data = request.query_params.get("td_data", dict())
            user_wallet_address = request.data.get("user_wallet_address", None)
            if user_wallet_address is None:
                raise rest_framework.exceptions.ParseError(
                    "user_wallet_address is a required field"
                )

            self.wallet_is_valid(user_profile, user_wallet_address, token_distribution)

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

            validator = TokenDistributionValidator(
                token_distribution,
                user_profile,
                td_data,
                request=request,
            )
            validator.is_valid()

            is_unitap_pass_user, user_unitap_pass_list = self.check_unitap_pass_share(
                token_distribution, user_profile
            )

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
                    token_distribution_id=token_distribution.pk,
                    user_wallet_address=user_wallet_address,
                    is_unitap_pass_share=is_unitap_pass_user,
                )
                # TODO: be careful about race condition
                token_distribution.used_unitap_pass_list.extend(user_unitap_pass_list)
                token_distribution.save(update_fields=["used_unitap_pass_list"])

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
        td_data = request.query_params.get("td_data", dict())

        reversed_constraints = td.reversed_constraints_list
        response_constraints = []

        validator = TokenDistributionValidator(
            td, user_profile, td_data, request=request
        )
        validated_constraints = validator.check_user_permissions(raise_exception=False)
        for c_pk, data in validated_constraints.items():
            response_constraints.append(
                {
                    **ConstraintSerializer(Constraint.objects.get(pk=c_pk)).data,
                    **data,
                    "is_reversed": True if str(c_pk) in reversed_constraints else False,
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


class ExtendTokenDistribution(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TokenDistributionSerializer

    def get(self, request: Request, pk):
        distribution_pk = pk
        try:
            distribution = TokenDistribution.objects.get(pk=distribution_pk)
        except TokenDistribution.DoesNotExist:
            raise Http404(
                f"Token distribution with pk {distribution_pk} Does not Exist"
            )
        if distribution.status != TokenDistribution.Status.VERIFIED:
            raise rest_framework.exceptions.PermissionDenied(
                "Token distribution is not verified"
            )
        if distribution.distributor_profile != request.user.profile:
            raise rest_framework.exceptions.PermissionDenied(
                "You are not owner of distribution"
            )
        distribution.check_for_extension = True
        distribution.save()
        return Response(
            {
                "success": True,
                "data": TokenDistributionSerializer(instance=distribution).data,
            }
        )


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
