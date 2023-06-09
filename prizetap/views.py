from rest_framework.generics import ListAPIView
from .models import Raffle
from .serializers import RaffleSerializer


class RaffleListView(ListAPIView):
    queryset = Raffle.objects.filter(is_active=True)
    serializer_class = RaffleSerializer
