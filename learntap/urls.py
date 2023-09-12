from django.urls import path
from .views import *

urlpatterns = [
    path("mission-list/", MissionsListView.as_view(), name="mission-list"),
    path("tag-list/", TagsListView.as_view(), name="tag-list"),
    path("mission/<int:pk>/", MissionRetrieveView.as_view(), name="mission"),
    path("task/<int:pk>/verify/", TaskVerificationView.as_view(), name="task-verify"),
]
