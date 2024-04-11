from django.contrib import admin

from core.admin import UserConstraintBaseAdmin
from .models import UserAnalytics


admin.site.register(UserAnalytics)
