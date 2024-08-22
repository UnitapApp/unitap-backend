"""brightIDfaucet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from faucet.views import artwork_view

admin.site.site_header = "Unitap Administration"
admin.site.index_title = "Unitap Administration"
admin.site.site_title = "Unitap Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("pass/art/<int:token_id>/", artwork_view),
    path("api/gastap/", include("faucet.urls")),
    path("api/auth/", include("authentication.urls")),
    path("api/tokentap/", include("tokenTap.urls")),
    path("api/prizetap/", include("prizetap.urls")),
    path("api/analytics/", include("analytics.urls")),
]
