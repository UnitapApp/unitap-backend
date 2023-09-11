from .models import *
from .serializers import *
from rest_framework.generics import ListAPIView


class TagsListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class MissionsListView(ListAPIView):
    queryset = (
        Mission.objects.filter(is_active=True)
        .order_by("-created_at")
        .order_by("-is_promoted")
    )
    serializer_class = MissionSerializer
