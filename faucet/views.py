from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView
import uuid

from faucet.serializers import CreateUserSerializer


class CreateUserView(CreateAPIView):
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        _uuid = uuid.uuid4()
        user = User.objects.create_user(username=str(_uuid))
        serializer.save(user=user, context_id=_uuid)
