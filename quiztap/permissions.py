from rest_framework.permissions import BasePermission

from quiztap.models import Competition
from quiztap.utils import is_user_eligible_to_participate


class IsEligibleToAnswer(BasePermission):
    """
    Permission to allow access if the
    user is eligible to answer questions in the competition.
    """

    def has_permission(self, request, view):
        competition_pk = request.data.get("competition")
        if competition_pk is None:
            return False
        user_profile = request.user.profile
        try:
            competition = Competition.objects.get(pk=competition_pk)
            return is_user_eligible_to_participate(user_profile, competition)
        except Competition.DoesNotExist:
            return False
