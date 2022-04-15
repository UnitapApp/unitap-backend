from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView
import uuid

from faucet.serializers import CreateUserSerializer


class CreateUserView(CreateAPIView):
    serializer_class = CreateUserSerializer