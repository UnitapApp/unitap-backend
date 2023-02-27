import http
from django.http import HttpResponse
from django.shortcuts import render
import requests
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from authentication.models import Profile
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response


# from authentication.helpers import verify_signature
from authentication.serializers import ProfileSerializer


class LoginView(ObtainAuthToken):
    def verify_signature(self, address, signed_message):
        # decrypt signed message using Ethereum signature scheme.
        # message = encode_defunct(text=address)

        return True

    def post(self, request, *args, **kwargs):
        address = request.GET.get("address")
        signature = request.GET.get("signature")

        # verify signature
        verified_signature = self.verify_signature(address, signature)

        if not verified_signature:
            return HttpResponse({"message": "Invalid signature"}, status=403)

        # get list of context ids from brightId
        # bright_response = requests.get(
        #     f"https://aura-node.brightid.org/brightid/v5/verifications/unitapTest/2?verification=Aura"
        # )
        # # decode response
        # bright_response = bright_response.json()
        # ls = bright_response["data"]["contextIds"]
        # print(ls)

        first_context_id = 1
        profile = Profile.objects.get_or_create(initial_context_id=first_context_id)
        user = profile.user

        # get auth token for the user
        token = Token.objects.get_or_create(user=user)

        # return token
        return Response({"token": token.key}, status=200)
