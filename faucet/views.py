from django.contrib.auth.models import User
from django.http import Http404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
import uuid

from faucet.models import BrightUser
from faucet.serializers import UserSerializer


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer


class GetVerificationUrlView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        address = self.kwargs.get('address')
        try:
            return BrightUser.objects.get(address=address)
        except BrightUser.DoesNotExist:
            if address is not None:
                return BrightUser.get_or_create(address)

            raise Http404

