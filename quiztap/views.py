from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone

from authentication.permissions import IsMeetVerified
from core.filters import ChainFilterBackend, IsOwnerFilterBackend, StatusFilterBackend
from core.paginations import StandardResultsSetPagination
from quiztap.filters import CompetitionFilter, NestedCompetitionFilter
from quiztap.models import Competition, Question, UserAnswer, UserCompetition
from quiztap.permissions import IsEligibleToAnswer
from quiztap.serializers import (
    CompetitionSerializer,
    QuestionSerializer,
    UserAnswerSerializer,
    UserCompetitionSerializer,
)


class CompetitionViewList(ListAPIView):
    filter_backends = [ChainFilterBackend, StatusFilterBackend]
    queryset = Competition.objects.filter(is_active=True).order_by("-created_at")
    pagination_class = StandardResultsSetPagination
    serializer_class = CompetitionSerializer


class CompetitionView(RetrieveAPIView):
    queryset = Competition.objects.filter(is_active=True)
    serializer_class = CompetitionSerializer


class QuestionView(RetrieveAPIView):
    http_method_names = ["get"]
    serializer_class = QuestionSerializer
    # queryset = Question.objects.filter(can_be_shown=True)
    queryset = Question.objects.all()


class EnrollInCompetitionView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMeetVerified]
    filter_backends = [IsOwnerFilterBackend, CompetitionFilter]
    pagination_class = StandardResultsSetPagination
    queryset = UserCompetition.objects.all()
    serializer_class = UserCompetitionSerializer

    def perform_create(self, serializer):
        serializer.save(user_profile=self.request.user.profile)


class UserAnswerView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsMeetVerified, IsEligibleToAnswer]
    serializer_class = UserAnswerSerializer
    filter_backends = [IsOwnerFilterBackend, NestedCompetitionFilter]
    queryset = UserAnswer.objects.all()


    def get_queryset(self):
        return self.queryset.filter(
            competition__start_at__gte=timezone.now()
        )

    def perform_create(self, serializer):
        serializer.save()
