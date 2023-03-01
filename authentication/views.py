from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from authentication.models import UserProfile, Wallet
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from authentication.helpers import (
    BRIGHTID_SOULDBOUND_INTERFACE,
    verify_signature_eth_scheme,
)
from authentication.serializers import ProfileSerializer, WalletSerializer
from brightIDfaucet.settings import BRIGHT_ID_INTERFACE


class SponsorshipView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        address = request.data.get("address")

        if BRIGHT_ID_INTERFACE.sponsor(str(address)):
            return Response({"message": "Sponsorship successful"}, status=200)
        else:
            return Response({"message": "Sponsorship failed"}, status=403)


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # TODO or should it be address, signature?
        address = request.data.get("username")
        signature = request.data.get("password")

        # verify signature
        verified_signature = verify_signature_eth_scheme(address, signature)

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

        if meet_context_ids is not None:
            context_ids = meet_context_ids
        elif aura_context_ids is not None:
            context_ids = aura_context_ids
        else:
            return Response({"message": "User is nothing verified"}, status=403)

        first_context_id = context_ids[-1]
        profile = UserProfile.objects.get_or_create(first_context_id=first_context_id)
        user = profile.user

        # get auth token for the user
        token, bol = Token.objects.get_or_create(user=user)
        print("token", token)

        # return Response({"token": token.key}, status=200)
        # return token and profile using profile serializer for profile
        return Response(
            {"token": token.key, "profile": ProfileSerializer(profile).data}, status=200
        )


class SetWalletAddressView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        address = request.data.get("address")
        wallet_type = request.data.get("wallet_type")

        # get user profile
        user_profile = request.user.profile

        try:
            # check if wallet already exists
            Wallet.objects.get(user_profile=user_profile, wallet_type=wallet_type)
            return Response(
                {"message": f"{wallet_type} wallet address already set"}, status=403
            )
        # TODO check for duplicate addresses
        except Wallet.DoesNotExist:
            # create wallet
            Wallet.objects.create(
                user_profile=user_profile, wallet_type=wallet_type, address=address
            )
            return Response(
                {"message": f"{wallet_type} wallet address set"}, status=200
            )


class GetWalletAddressView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wallet_type = request.data.get("wallet_type")

        # get user profile
        user_profile = request.user.profile

        try:
            # check if wallet already exists
            wallet = Wallet.objects.get(
                user_profile=user_profile, wallet_type=wallet_type
            )
            return Response({"address": wallet.address}, status=200)

        except Wallet.DoesNotExist:
            return Response(
                {"message": f"{wallet_type} wallet address not set"}, status=403
            )


class DeleteWalletAddressView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wallet_type = request.data.get("wallet_type")

        # get user profile
        user_profile = request.user.profile

        try:
            # check if wallet already exists
            wallet = Wallet.objects.get(
                user_profile=user_profile, wallet_type=wallet_type
            )
            wallet.delete()
            return Response(
                {"message": f"{wallet_type} wallet address deleted"}, status=200
            )

        except Wallet.DoesNotExist:
            return Response(
                {"message": f"{wallet_type} wallet address not set"}, status=403
            )


class GetWalletsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletSerializer

    def get_queryset(self):
        return Wallet.objects.filter(user_profile=self.request.user.profile)


class GetProfileView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile
