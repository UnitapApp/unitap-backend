from rest_framework.generics import ListAPIView, RetrieveAPIView

from core.filters import ChainFilterBackend
from quiztap.models import Competition, Question
from quiztap.serializers import CompetitionSerializer, QuestionSerializer


class CompetitionViewList(ListAPIView):
    filter_backends = [ChainFilterBackend]
    queryset = Competition.objects.filter(is_active=True)
    serializer_class = CompetitionSerializer


class QuestionView(RetrieveAPIView):
    http_method_names = ["get"]
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
