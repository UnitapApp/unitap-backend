from django.urls import path

from quiztap.views import (
    CompetitionView,
    CompetitionViewList,
    EnrollInCompetitionView,
    QuestionView,
    UserAnswerView,
)

urlpatterns = [
    path("competitions/", CompetitionViewList.as_view(), name="competition-list"),
    path("competitions/<int:pk>/", CompetitionView.as_view(), name="competition"),
    path("questions/<int:pk>/", QuestionView.as_view(), name="question"),
    path(
        "competitions/enroll/",
        EnrollInCompetitionView.as_view(),
        name="enroll-competition",
    ),
    path(
        "competitions/submit-answer/",
        UserAnswerView.as_view(),
        name="user-competition-answers",
    ),
]
