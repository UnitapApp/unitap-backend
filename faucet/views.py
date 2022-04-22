import rest_framework.exceptions
from django.http import Http404
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from faucet.faucet_manager.claim_manager import ClaimManagerFactory
from faucet.models import BrightUser, Chain, ClaimReceipt
from faucet.serializers import UserSerializer, ChainSerializer, ReceiptSerializer


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


class ClaimMaxView(APIView):
    def get_user(self) -> BrightUser:
        address = self.kwargs.get('address', None)
        return BrightUser.objects.get(address=address)

    def check_user_is_verified(self):
        _is_verified = self.get_user().verification_status == BrightUser.VERIFIED
        if not _is_verified:
            raise rest_framework.exceptions.NotAcceptable

    def get_chain(self) -> Chain:
        chain_pk = self.kwargs.get('chain_pk', None)
        return Chain.objects.get(pk=chain_pk)

    def get_claim_manager(self):
        return ClaimManagerFactory(self.get_chain(), self.get_user()).get_manager()

    def claim_max(self) -> ClaimReceipt:
        manager = self.get_claim_manager()
        max_credit = manager.get_credit_strategy().get_unclaimed()
        try:
            assert max_credit > 0
            return manager.claim(max_credit)
        except AssertionError as e:
            raise rest_framework.exceptions.PermissionDenied

    def post(self, request, *args, **kwargs):
        self.check_user_is_verified()
        receipt = self.claim_max()
        return Response(ReceiptSerializer(instance=receipt).data)
