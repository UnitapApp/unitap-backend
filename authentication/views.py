import http
from django.http import HttpResponse
from django.shortcuts import render
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from authentication.models import Profile, Wallet
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


class SetWalletAddressView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        address = request.data.get("address")
        wallet_type = request.data.get("wallet_type")

        # get user profile
        profile = request.user.profile

        try:
            # check if wallet already exists
            Wallet.objects.get(profile=profile, wallet_type=wallet_type)
            return Response(
                {"message": f"{wallet_type} wallet address already set"}, status=403
            )

        except Wallet.DoesNotExist:
            # create wallet
            Wallet.objects.create(
                profile=profile, wallet_type=wallet_type, address=address
            )
            return Response(
                {"message": f"{wallet_type} wallet address set"}, status=200
            )


class GetWalletAddressView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wallet_type = request.data.get("wallet_type")

        # get user profile
        profile = request.user.profile

        try:
            # check if wallet already exists
            wallet = Wallet.objects.get(profile=profile, wallet_type=wallet_type)
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
        profile = request.user.profile

        try:
            # check if wallet already exists
            wallet = Wallet.objects.get(profile=profile, wallet_type=wallet_type)
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

    def get(self, request, *args, **kwargs):
        # get user profile
        profile = request.user.profile

        wallets = Wallet.objects.filter(profile=profile)
        wallets = [{wallet.wallet_type: wallet.address} for wallet in wallets]

        return Response({"wallets": wallets}, status=200)


# class SetEVMWalletAddressView(CreateAPIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         address = request.data.get("address")
#         # get user profile
#         profile = request.user.profile
#         try:
#             # check if EVM wallet already exists
#             EVMWallet.objects.get(profile=profile)
#             return Response({"message": "EVM wallet address already set"}, status=403)

#         except EVMWallet.DoesNotExist:
#             # create EVM wallet
#             EVMWallet.objects.create(profile=profile, address=address)
#             return Response({"message": "EVM wallet address set"}, status=200)


# class SetSolanaWalletAddressView(CreateAPIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         address = request.data.get("address")
#         # get user profile
#         profile = request.user.profile
#         try:
#             # check if Solana wallet already exists
#             SolanaWallet.objects.get(profile=profile)
#             return Response(
#                 {"message": "Solana wallet address already set"}, status=403
#             )

#         except SolanaWallet.DoesNotExist:
#             # create Solana wallet
#             SolanaWallet.objects.create(profile=profile, address=address)
#             return Response({"message": "Solana wallet address set"}, status=200)


# class SetBitcoinLightningWalletAddressView(CreateAPIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         address = request.data.get("address")
#         # get user profile
#         profile = request.user.profile
#         try:
#             # check if Bitcoin Lightning wallet already exists
#             BitcoinLightningWallet.objects.get(profile=profile)
#             return Response(
#                 {"message": "Bitcoin Lightning wallet address already set"}, status=403
#             )

#         except BitcoinLightningWallet.DoesNotExist:
#             # create Bitcoin Lightning wallet
#             BitcoinLightningWallet.objects.create(profile=profile, address=address)
#             return Response(
#                 {"message": "Bitcoin Lightning wallet address set"}, status=200
#             )


# class GetEVMWalletAddressView(RetrieveAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # get user profile
#         profile = request.user.profile
#         try:
#             # get EVM wallet
#             evm_wallet = EVMWallet.objects.get(profile=profile)
#             return Response({"address": evm_wallet.address}, status=200)

#         except EVMWallet.DoesNotExist:
#             return Response({"message": "EVM wallet address not set"}, status=404)


# class GetSolanaWalletAddressView(RetrieveAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # get user profile
#         profile = request.user.profile
#         try:
#             # get Solana wallet
#             solana_wallet = SolanaWallet.objects.get(profile=profile)
#             return Response({"address": solana_wallet.address}, status=200)

#         except SolanaWallet.DoesNotExist:
#             return Response({"message": "Solana wallet address not set"}, status=404)


# class GetBitcoinLightningWalletAddressView(RetrieveAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # get user profile
#         profile = request.user.profile
#         try:
#             # get Bitcoin Lightning wallet
#             bitcoin_lightning_wallet = BitcoinLightningWallet.objects.get(
#                 profile=profile
#             )
#             return Response({"address": bitcoin_lightning_wallet.address}, status=200)

#         except BitcoinLightningWallet.DoesNotExist:
#             return Response(
#                 {"message": "Bitcoin Lightning wallet address not set"}, status=404
#             )


# class DeleteEVMWalletAddressView(RetrieveAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # get user profile
#         profile = request.user.profile
#         try:
#             # get EVM wallet
#             evm_wallet = EVMWallet.objects.get(profile=profile)
#             evm_wallet.delete()
#             return Response({"message": "EVM wallet address deleted"}, status=200)

#         except EVMWallet.DoesNotExist:
#             return Response({"message": "EVM wallet address not set"}, status=404)


# class DeleteSolanaWalletAddressView(RetrieveAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # get user profile
#         profile = request.user.profile
#         try:
#             # get Solana wallet
#             solana_wallet = SolanaWallet.objects.get(profile=profile)
#             solana_wallet.delete()
#             return Response({"message": "Solana wallet address deleted"}, status=200)

#         except SolanaWallet.DoesNotExist:
#             return Response({"message": "Solana wallet address not set"}, status=404)


# class DeleteBitcoinLightningWalletAddressView(RetrieveAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # get user profile
#         profile = request.user.profile
#         try:
#             # get Bitcoin Lightning wallet
#             bitcoin_lightning_wallet = BitcoinLightningWallet.objects.get(
#                 profile=profile
#             )
#             bitcoin_lightning_wallet.delete()
#             return Response(
#                 {"message": "Bitcoin Lightning wallet address deleted"}, status=200
#             )

#         except BitcoinLightningWallet.DoesNotExist:
#             return Response(
#                 {"message": "Bitcoin Lightning wallet address not set"}, status=404
#             )


# class GetWalletsView(RetrieveAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         # get user profile
#         profile = request.user.profile
#         try:
#             # get EVM wallet
#             evm_wallet = EVMWallet.objects.get(profile=profile)
#             evm_wallet_address = evm_wallet.address
#         except EVMWallet.DoesNotExist:
#             evm_wallet_address = None

#         try:
#             # get Solana wallet
#             solana_wallet = SolanaWallet.objects.get(profile=profile)
#             solana_wallet_address = solana_wallet.address
#         except SolanaWallet.DoesNotExist:
#             solana_wallet_address = None

#         try:
#             # get Bitcoin Lightning wallet
#             bitcoin_lightning_wallet = BitcoinLightningWallet.objects.get(
#                 profile=profile
#             )
#             bitcoin_lightning_wallet_address = bitcoin_lightning_wallet.address
#         except BitcoinLightningWallet.DoesNotExist:
#             bitcoin_lightning_wallet_address = None

#         return Response(
#             {
#                 "evm_wallet_address": evm_wallet_address,
#                 "solana_wallet_address": solana_wallet_address,
#                 "bitcoin_lightning_wallet_address": bitcoin_lightning_wallet_address,
#             },
#             status=200,
#         )
