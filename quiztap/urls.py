from django.urls import path

from quiztap.views import CompetitionViewList, QuestionView

urlpatterns = [
    path("competitions/", CompetitionViewList.as_view(), name="competition-list"),
    path("questions/<int:pk>", QuestionView.as_view(), name="question"),
]
