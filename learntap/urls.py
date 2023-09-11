from django.urls import path
from .views import *

urlpatterns = [
    path("mission-list/", MissionsListView.as_view(), name="mission-list"),
    path("tag-list/", TagsListView.as_view(), name="tag-list"),
]
