from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from authentication.models import (
    BrightIDConnection,
    GitcoinPassportConnection,
    UserProfile,
)



class GetUserAnalytics(APIView):
    def get(self, request : Request) -> Response:
        # check cache
        analytics = cache.get("analytics_users_count")
        if analytics is None:
            all_users_count = UserProfile.user_count()
            brightid_users_count = BrightIDConnection.objects.all().count()
            gitcoinpassport_users_count = (
                GitcoinPassportConnection.objects.all().count()
            ) 
            analytics = {
                "all_users_count": all_users_count,
                "brightid_users_count": brightid_users_count,
                "gitcoinpassport_users_count": gitcoinpassport_users_count,
            }
            # set cache
            cache.set("analytics_users_count", analytics, timeout=10 * 60)
        return Response(analytics)