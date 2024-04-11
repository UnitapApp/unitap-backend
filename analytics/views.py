import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserAnalytics

# class UserAnalytics():
#     def get(self, request, *args, **kwargs):
#         return Response({"count": UserProfile.user_count()}, status=200)

@api_view(['GET'])
def getUserAnalytics(request):
    records = UserAnalytics.objects.all().values()
    return Response(records,status=status.HTTP_201_CREATED)
    
