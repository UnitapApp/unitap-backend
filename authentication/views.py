import http
from django.http import HttpResponse
from django.shortcuts import render
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from authentication.models import (
    Profile,
    EVMWallet,
    SolanaWallet,
    BitcoinLightningWallet,
)
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from authentication.helpers import (
    BRIGHTID_SOULDBOUND_INTERFACE,
    verify_signature_eth_scheme,
)


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # TODO or should it be address, signature?
        address = request.data.get("username")
        signature = request.data.get("password")

        # print("address", address)
        # print("signature", signature)

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
        profile = Profile.objects.get_or_create(first_context_id=first_context_id)
        user = profile.user

        # get auth token for the user
        token, bol = Token.objects.get_or_create(user=user)
        print("token", token)

        # return token
        return Response({"token": token.key}, status=200)


class SetEVMWalletAddressView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        address = request.data.get("address")
        # get user profile
        profile = request.user.profile
        try:
            # check if EVM wallet already exists
            EVMWallet.objects.get(profile=profile)
            return Response({"message": "EVM wallet address already set"}, status=403)

        except EVMWallet.DoesNotExist:
            # create EVM wallet
            EVMWallet.objects.create(profile=profile, address=address)
            return Response({"message": "EVM wallet address set"}, status=200)


class SetSolanaWalletAddressView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        address = request.data.get("address")
        # get user profile
        profile = request.user.profile
        try:
            # check if Solana wallet already exists
            SolanaWallet.objects.get(profile=profile)
            return Response(
                {"message": "Solana wallet address already set"}, status=403
            )

        except SolanaWallet.DoesNotExist:
            # create Solana wallet
            SolanaWallet.objects.create(profile=profile, address=address)
            return Response({"message": "Solana wallet address set"}, status=200)


class SetBitcoinLightningWalletAddressView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        address = request.data.get("address")
        # get user profile
        profile = request.user.profile
        try:
            # check if Bitcoin Lightning wallet already exists
            BitcoinLightningWallet.objects.get(profile=profile)
            return Response(
                {"message": "Bitcoin Lightning wallet address already set"}, status=403
            )

        except BitcoinLightningWallet.DoesNotExist:
            # create Bitcoin Lightning wallet
            BitcoinLightningWallet.objects.create(profile=profile, address=address)
            return Response(
                {"message": "Bitcoin Lightning wallet address set"}, status=200
            )


class GetEVMWalletAddressView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # get user profile
        profile = request.user.profile
        try:
            # get EVM wallet
            evm_wallet = EVMWallet.objects.get(profile=profile)
            return Response({"address": evm_wallet.address}, status=200)

        except EVMWallet.DoesNotExist:
            return Response({"message": "EVM wallet address not set"}, status=404)


class GetSolanaWalletAddressView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # get user profile
        profile = request.user.profile
        try:
            # get Solana wallet
            solana_wallet = SolanaWallet.objects.get(profile=profile)
            return Response({"address": solana_wallet.address}, status=200)

        except SolanaWallet.DoesNotExist:
            return Response({"message": "Solana wallet address not set"}, status=404)


class GetBitcoinLightningWalletAddressView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # get user profile
        profile = request.user.profile
        try:
            # get Bitcoin Lightning wallet
            bitcoin_lightning_wallet = BitcoinLightningWallet.objects.get(
                profile=profile
            )
            return Response({"address": bitcoin_lightning_wallet.address}, status=200)

        except BitcoinLightningWallet.DoesNotExist:
            return Response(
                {"message": "Bitcoin Lightning wallet address not set"}, status=404
            )


class DeleteEVMWalletAddressView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # get user profile
        profile = request.user.profile
        try:
            # get EVM wallet
            evm_wallet = EVMWallet.objects.get(profile=profile)
            evm_wallet.delete()
            return Response({"message": "EVM wallet address deleted"}, status=200)

        except EVMWallet.DoesNotExist:
            return Response({"message": "EVM wallet address not set"}, status=404)


class DeleteSolanaWalletAddressView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # get user profile
        profile = request.user.profile
        try:
            # get Solana wallet
            solana_wallet = SolanaWallet.objects.get(profile=profile)
            solana_wallet.delete()
            return Response({"message": "Solana wallet address deleted"}, status=200)

        except SolanaWallet.DoesNotExist:
            return Response({"message": "Solana wallet address not set"}, status=404)


class DeleteBitcoinLightningWalletAddressView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # get user profile
        profile = request.user.profile
        try:
            # get Bitcoin Lightning wallet
            bitcoin_lightning_wallet = BitcoinLightningWallet.objects.get(
                profile=profile
            )
            bitcoin_lightning_wallet.delete()
            return Response(
                {"message": "Bitcoin Lightning wallet address deleted"}, status=200
            )

        except BitcoinLightningWallet.DoesNotExist:
            return Response(
                {"message": "Bitcoin Lightning wallet address not set"}, status=404
            )
