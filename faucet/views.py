from django.contrib.auth.models import User
from django.http import Http404
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
import uuid

from faucet.models import BrightUser, Chain
from faucet.serializers import UserSerializer, ChainSerializer


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


class ChainListView(ListAPIView):
    serializer_class = ChainSerializer
    queryset = Chain.objects.all()
