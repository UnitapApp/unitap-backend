from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.helpers import (
    BRIGHTID_SOULDBOUND_INTERFACE,
    is_username_valid_and_available,
    verify_signature_eth_scheme,
)
from authentication.models import UserProfile, Wallet
from authentication.serializers import (
    MessageResponseSerializer,
    ProfileSerializer,
    UserHistoryCountSerializer,
    UsernameRequestSerializer,
    WalletSerializer,
)
from core.filters import IsOwnerFilterBackend


class UserProfileCountView(ListAPIView):
    def get(self, request, *args, **kwargs):
        return Response({"count": UserProfile.user_count()}, status=200)


class SponsorView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        address = request.data.get("address", None)
        if not address:
            return Response({"message": "Invalid request"}, status=403)

        verification_link = BRIGHTID_SOULDBOUND_INTERFACE.create_verification_link(
            address
        )
        qr_content = BRIGHTID_SOULDBOUND_INTERFACE.create_qr_content(address)

        if BRIGHTID_SOULDBOUND_INTERFACE.check_sponsorship(address):
            return Response(
                {
                    "message": "User is already sponsored.",
                    "verification_link": verification_link,
                    "qr_content": qr_content,
                },
                status=200,
            )

        if BRIGHTID_SOULDBOUND_INTERFACE.sponsor(str(address)) is not True:
            return Response({"message": "something went wrong."}, status=403)

        return Response(
            {
                "message": "User is being sponsored.",
                "verification_link": verification_link,
                "qr_content": qr_content,
            },
            status=200,
        )


class LoginView(APIView):
    serializer_class = ProfileSerializer

    def post(self, request, *args, **kwargs):
        address = request.data.get("username", None)
        signature = request.data.get("password", None)
        if not address or not signature:
            return Response({"message": "Invalid request"}, status=403)

        is_sponsored = BRIGHTID_SOULDBOUND_INTERFACE.check_sponsorship(address)
        if not is_sponsored:
            if BRIGHTID_SOULDBOUND_INTERFACE.sponsor(str(address)) is not True:
                return Response(
                    {
                        "message": "We are in the process of sponsoring you. \
                            Please try again in five minutes."
                    },
                    status=403,
                )
            else:
                return Response(
                    {
                        "message": "We have requested to sponsor you on BrightID\
                            . Please try again in five minutes."
                    },
                    status=409,
                )

        verified_signature = verify_signature_eth_scheme(address, address, signature)
        if not verified_signature:
            return Response({"message": "Invalid signature"}, status=403)

        (
            is_meet_verified,
            meet_context_ids,
        ) = BRIGHTID_SOULDBOUND_INTERFACE.get_verification_status(address, "Meet")
        (
            is_aura_verified,
            aura_context_ids,
        ) = BRIGHTID_SOULDBOUND_INTERFACE.get_verification_status(address, "Aura")

        context_ids = []

        if is_meet_verified is False and is_aura_verified is False:
            if meet_context_ids == 3:  # is not verified
                context_ids = address
            elif aura_context_ids == 4:  # is not linked
                return Response(
                    {
                        "message": "Something went wrong with the linking process. \
                            please link BrightID with Unitap.\n"
                        "If the problem persists, clear your browser cache \
                            and try again."
                    },
                    status=403,
                )

        elif is_meet_verified is True or is_aura_verified is True:
            if meet_context_ids is not None:
                context_ids = meet_context_ids
            elif aura_context_ids is not None:
                context_ids = aura_context_ids

        first_context_id = context_ids[-1]
        profile = UserProfile.objects.get_or_create(first_context_id=first_context_id)
        user = profile.user

        # get auth token for the user
        token, bol = Token.objects.get_or_create(user=user)
        print("token", token)

        return Response(ProfileSerializer(profile).data, status=200)


class SetUsernameView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=UsernameRequestSerializer,
        responses={
            200: openapi.Response(
                description="Username successfully Set",
                schema=MessageResponseSerializer(),
            ),
            400: openapi.Response(
                description="Bad request", schema=MessageResponseSerializer()
            ),
            403: openapi.Response(
                description="This username already exists.\ntry another one.",
                schema=MessageResponseSerializer(),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        request_serializer = UsernameRequestSerializer(data=request.data)

        if request_serializer.is_valid():
            username = request_serializer.validated_data.get("username")
            user_profile = request.user.profile

            s, a, b = is_username_valid_and_available(username)
            if not s:
                return Response(
                    MessageResponseSerializer({"message": "Invalid username"}).data,
                    status=400,
                )

            try:
                user_profile.username = username
                user_profile.save()
                return Response(
                    MessageResponseSerializer(
                        {"message": "Username successfully Set"}
                    ).data,
                    status=200,
                )

            except IntegrityError:
                return Response(
                    MessageResponseSerializer(
                        {"message": "This username already exists.\ntry another one."}
                    ).data,
                    status=403,
                )

        else:
            return Response(request_serializer.errors, status=400)


class CheckUsernameView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=UsernameRequestSerializer,
        responses={
            200: openapi.Response(
                description="<Username> is available",
                schema=MessageResponseSerializer(),
            ),
            400: openapi.Response(
                description="Bad request",
                schema=MessageResponseSerializer(),
            ),
            409: openapi.Response(
                description="The username <username> is already in use.",
                schema=MessageResponseSerializer(),
            ),
            403: openapi.Response(
                description="Username must be more than 2 characters, contain at least"
                " one letter, and only contain letters, digits and @/./+/-/_.",
                schema=MessageResponseSerializer(),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        request_serializer = UsernameRequestSerializer(data=request.data)

        if request_serializer.is_valid():
            username = request_serializer.validated_data.get("username")

            # if UserProfile.objects.filter(username=username).exists():
            #     return Response(
            #         MessageResponseSerializer(
            #             {"message": "This username already exists.\ntry another one."}
            #         ).data,
            #         status=403,
            #     )
            # else:
            #     return Response(
            #         MessageResponseSerializer(
            #             {"message": "Username is available"}
            #         ).data,
            #         status=200,
            #     )

            status, message, flag = is_username_valid_and_available(username)

            if status:
                return Response(
                    MessageResponseSerializer({"message": message}).data, status=200
                )
            return Response(
                MessageResponseSerializer({"message": message}).data,
                status=403 if flag == "validation_error" else 409,
            )

        else:
            return Response(request_serializer.errors, status=400)


class WalletListCreateView(ListCreateAPIView):
    queryset = Wallet.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = WalletSerializer
    filter_backends = [IsOwnerFilterBackend, DjangoFilterBackend]
    filterset_fields = ["wallet_type"]

    def perform_create(self, serializer):
        serializer.save(user_profile=self.request.user.profile)


class UserHistoryCountView(RetrieveAPIView):
    permissions = [IsAuthenticated]
    serializer_class = UserHistoryCountSerializer

    def get_object(self):
        from faucet.models import ClaimReceipt

        user_profile = self.request.user.profile
        data = {
            "gas_claim": user_profile.claims.filter(
                _status=ClaimReceipt.VERIFIED
            ).count(),
            "token_claim": user_profile.tokentap_claims.filter(
                status=ClaimReceipt.VERIFIED
            ).count(),
            "raffle_win": user_profile.raffle_entries.count(),
        }
        return data


class GetProfileView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile
