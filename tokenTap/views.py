import json
import logging
from django.http import FileResponse
import os
import rest_framework.exceptions
from django.http import Http404
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from authentication.models import UserProfile, Wallet
from faucet.models import Chain, GlobalSettings
from tokenTap.models import TokenDistribution
from tokenTap.serializers import TokenDistributionSerializer


class TokenDistributionListView(ListAPIView):
    serializer_class = TokenDistributionSerializer
    queryset = TokenDistribution.objects.all()
