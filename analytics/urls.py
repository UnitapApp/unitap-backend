from django.contrib import admin
from django.urls import include, path

from analytics.views import getUserAnalytics

admin.site.site_header = "Unitap Administration"
admin.site.index_title = "Unitap Administration"
admin.site.site_title = "Unitap Administration"

app_name = "ANALYTICS"

urlpatterns = [
    path("user-analytics/", getUserAnalytics.as_view(), name="get-user-analytics"),
]
