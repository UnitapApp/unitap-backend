from .models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated


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


class MissionRetrieveView(RetrieveAPIView):
    queryset = Mission.objects.filter(is_active=True)
    serializer_class = MissionFullSerializer
    lookup_field = "pk"


class TaskVerificationView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        pass
        # get user data
        # check if its not already verified
        # check if verification mutex is not locked
        # verify
        # update user progress
        # update user XP
        # return ok or not ok
