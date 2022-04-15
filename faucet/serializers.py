from rest_framework import serializers

from faucet.models import BrightUser


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrightUser
        fields = ['context_id', ]