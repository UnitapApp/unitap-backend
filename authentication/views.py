import json
import logging

from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException, ParseError, ValidationError
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from authentication.helpers import (
    BRIGHTID_SOULDBOUND_INTERFACE,
    is_username_valid_and_available,
    verify_login_signature,
    verify_signature_eth_scheme,
)
from authentication.models import (
    BrightIDConnection,
    ENSConnection,
    ENSSaveError,
    GitcoinPassportSaveError,
    TwitterConnection,
    UserProfile,
    Wallet,
)
from authentication.permissions import IsOwner
from authentication.serializers import (
    ENSConnectionSerializer,
    GitcoinPassportConnectionSerializer,
    MessageResponseSerializer,
    ProfileSerializer,
    UserHistoryCountSerializer,
    UsernameRequestSerializer,
    WalletSerializer,
    thirdparty_connection_serializer,
)
from core.filters import IsOwnerFilterBackend
from core.thirdpartyapp import TwitterUtils


class UserProfileCountView(ListAPIView):
    def get(self, request, *args, **kwargs):
        return Response({"count": UserProfile.user_count()}, status=200)


class UserThirdPartyConnectionsView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        connections = self.request.user.profile.get_all_thirdparty_connections()

        return Response(thirdparty_connection_serializer(connections), status=200)


class CheckUserExistsView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "wallet_address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The wallet address of the user to check.",
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="User exists or not",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"exists": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
                ),
            ),
            403: openapi.Response(
                description="Invalid request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        wallet_address = request.data.get("wallet_address", None)
        if not wallet_address:
            return Response({"message": "Invalid request"}, status=403)

        user_exists = (
            UserProfile.objects.get_by_wallet_address(wallet_address) is not None
        )

        return Response({"exists": user_exists}, status=200)


class LoginRegisterView(CreateAPIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "wallet_address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The wallet address of the user to login/register.",
                ),
                "signature": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The signature of the wallet address.",
                ),
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The message signed by the wallet address.",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="User profile is returned",
                schema=ProfileSerializer(),
            ),
            400: openapi.Response(
                description="Invalid request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            403: openapi.Response(
                description="Invalid signature",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        wallet_address = request.data.get("wallet_address", None)
        signature = request.data.get("signature", None)
        message = request.data.get("message", None)
        if not wallet_address or not signature or not message:
            return Response({"message": "Invalid request"}, status=400)

        if not verify_login_signature(wallet_address, json.loads(message), signature):
            return Response({"message": "Invalid signature"}, status=403)

        try:
            user_profile = UserProfile.objects.get_or_create_with_wallet_address(
                wallet_address
            )
        except IntegrityError:
            return Response(
                {"message": "This wallet address is already registered."}, status=400
            )

        return Response(ProfileSerializer(user_profile).data, status=200)


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


class ConnectBrightIDView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The wallet address of the user to login/register.",
                ),
                "signature": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The signature of the wallet address.",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="User profile is returned",
                schema=ProfileSerializer(),
            ),
            400: openapi.Response(
                description="Invalid request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            403: openapi.Response(
                description="Invalid signature",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        address = request.data.get("address", None)
        signature = request.data.get("signature", None)
        if not address or not signature:
            return Response({"message": "Invalid request"}, status=403)

        profile = request.user.profile

        try:
            bic = BrightIDConnection.get_connection(profile)
            is_connected = bic.is_connected()
            if is_connected:
                return Response(
                    {"message": "You are already connected to BrightID"}, status=403
                )
        except BrightIDConnection.DoesNotExist:
            pass

        is_sponsored = BrightIDConnection.driver.check_sponsorship(address)
        if not is_sponsored:
            if BrightIDConnection.driver.sponsor(str(address)) is not True:
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
        ) = BrightIDConnection.driver.get_meets_verification_status(address)
        # (
        #     is_aura_verified,
        #     aura_context_ids,
        # ) = BrightIDConnection.driver.get_aura_verification_status(address)

        context_ids = []

        if is_meet_verified == False:  # noqa: E712
            if meet_context_ids == 3:  # is not verified
                context_ids = address
            # elif aura_context_ids == 4:  # is not linked
            #     return Response(
            #         {
            #             "message": "Something went wrong with the linking process. \
            #                 please link BrightID with Unitap.\n"
            #             "If the problem persists, clear your browser cache \
            #                            and try again."
            #         },
            #         status=403,
            #     )

        elif is_meet_verified == True:  # noqa: E712
            if meet_context_ids is not None:
                context_ids = meet_context_ids
            # elif aura_context_ids is not None:
            #     context_ids = aura_context_ids

        first_context_id = context_ids[-1]
        try:
            BrightIDConnection.objects.create(
                user_profile=profile, context_id=first_context_id
            )
        except IntegrityError:
            return Response(
                {
                    "message": "This BrightID account is already connected \
                    to another Unitap account."
                },
                status=400,
            )

        return Response(ProfileSerializer(profile).data, status=200)


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

        if is_meet_verified == False and is_aura_verified == False:  # noqa: E712
            if meet_context_ids == 3:  # is not verified
                context_ids = address
            elif aura_context_ids == 4:  # is not linked
                return Response(
                    {
                        "message": "Something went wrong with the linking process."
                        " please link BrightID with Unitap.\n"
                        "If the problem persists,"
                        " clear your browser cache and try again."
                    },
                    status=403,
                )

        elif is_meet_verified == True or is_aura_verified == True:  # noqa: E712
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


class GitcoinPassportConnectionView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GitcoinPassportConnectionSerializer

    @property
    def user_profile(self):
        return self.request.user.profile

    def perform_create(self, serializer):
        try:
            serializer.save(user_profile=self.user_profile)
        except GitcoinPassportSaveError as e:
            raise ValidationError({"address": str(e)})


class ENSConnectionView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ENSConnectionSerializer

    @property
    def user_profile(self):
        return self.request.user.profile

    def perform_create(self, serializer):
        try:
            serializer.save(user_profile=self.user_profile)
        except ValidationError as e:
            raise ValidationError({"address": str(e)})


class ENSDisconnectionView(DestroyAPIView):
    queryset = ENSConnection.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ENSConnectionSerializer


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
    # permission_classes = [IsAuthenticated]

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
                description="Username must be more than 3 characters, contain at least"
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

    def get_user_profile(self):
        return self.request.user.profile

    def perform_create(self, serializer):
        try:
            serializer.save(user_profile=self.get_user_profile())
        except IntegrityError:
            raise ValidationError({"address": "address already exists."})


class WalletView(RetrieveDestroyAPIView):
    queryset = Wallet.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = WalletSerializer
    filter_backends = [IsOwnerFilterBackend]

    def perform_destroy(self, instance):
        if len(instance.user_profile.wallets.all()) > 1:
            return super().perform_destroy(instance)
        raise ParseError("User has only one wallet!")


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


class TwitterOAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_profile(self):
        return self.request.user.profile

    def get(self, request, *args, **kwargs):
        try:
            url, request_token = TwitterUtils.get_authorization_url_and_token()
        except Exception as e:
            logging.error(f"Could not connect to twitter: {e}")
            raise APIException("Twitter did not respond")

        oauth_token = request_token.get("oauth_token")
        oauth_token_secret = request_token.get("oauth_token_secret")

        try:
            twitter_connection = TwitterConnection.objects.get(
                user_profile=self.get_user_profile()
            )
            twitter_connection.oauth_token = oauth_token
            twitter_connection.oauth_token_secret = oauth_token_secret
            twitter_connection.access_token = None
            twitter_connection.access_token_secret = None
            twitter_connection.save(
                update_fields=(
                    "oauth_token",
                    "oauth_token_secret",
                    "access_token",
                    "access_token_secret",
                )
            )
        except TwitterConnection.DoesNotExist:
            twitter_connection = TwitterConnection(
                oauth_token=oauth_token,
                oauth_token_secret=oauth_token_secret,
                user_profile=self.get_user_profile(),
            )
            twitter_connection.save()
        return Response({"url": url}, status=HTTP_200_OK)


class TwitterOAuthCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        oauth_token = request.query_params.get("oauth_token")
        oauth_verifier = request.query_params.get("oauth_verifier")

        if oauth_verifier is None and oauth_token is None:
            raise ParseError("You must set oauth_verifier and oauth_token ")

        try:
            twitter_connection = TwitterConnection.objects.get(oauth_token=oauth_token)
        except TwitterConnection.DoesNotExist:
            raise ParseError("TwitterConnection not found")

        try:
            access_token, access_token_secret = TwitterUtils.get_access_token(
                oauth_token=oauth_token,
                oauth_token_secret=twitter_connection.oauth_token_secret,
                oauth_verifier=oauth_verifier,
            )
        except Exception as e:
            logging.error(f"Could not connect to twitter: {e}")
            raise ParseError("Could not connect to twitter")

        twitter_connection.access_token = access_token
        twitter_connection.access_token_secret = access_token_secret

        twitter_connection.save(update_fields=("access_token", "access_token_secret"))

        return Response({}, HTTP_200_OK)
