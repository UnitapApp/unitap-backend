import json
from learntap.validators import TaskVerificationValidator
from .models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from .helpers import UserProgressManager


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


class StartMissionView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        mission = Mission.objects.get(pk=kwargs["pk"])
        profile = request.user.profile
        UserProgressManager.start_mission(profile, mission)
        return Response({"detail": "Mission started successfully"}, status=200)


class TaskVerificationView(CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # get user data
        user_data = request.data.get("user_data", None)
        if user_data:
            try:
                user_data = json.loads(user_data)
            except:
                return Response({"error": "Invalid user data"}, status=400)
        profile = request.user.profile
        task = Task.objects.get(pk=kwargs["pk"])

        # check if verification mutex is not locked -> {user_id: task_id}
        is_verifying = cache.get(f"task_verification:{profile.pk}")
        if is_verifying:
            return Response(
                {"error": "Verification is already in progress"}, status=400
            )
        else:
            cache.set(f"task_verification:{profile.pk}", task.pk, 120)

        # verify
        validator = TaskVerificationValidator(
            user_profile=profile, task=task, user_data=user_data
        )
        validator.is_valid(user_data)

        # update user progress
        UserProgressManager.update_user_progress(profile, task)

        # update user XP TODO

        cache.delete(f"task_verification:{profile.pk}")
        return Response({"detail": "Task verified successfully"}, status=200)
