from django.core.cache import cache
from django.utils import timezone
from rest_framework.permissions import BasePermission

from quiztap.models import Competition, UserCompetition


class IsEligibleToAnswer(BasePermission):
    """
    Permission to allow access if the
    user is eligible to answer questions in the competition.
    """

    def has_permission(self, request, view):
        competition_pk = request.data.get("competition")
        if competition_pk is None:
            return False
        user_profile = request.user.user_profile
        try:
            competition = Competition.objects.get(pk=competition_pk)
            user_competition_pk = UserCompetition.objects.get(
                user_profile=user_profile, competition__pk=competition
            ).pk
        except (Competition.DoesNotExist, UserCompetition.DoesNotExist):
            return False
        eligible_users = cache.get(f"comp_{competition_pk}_eligible_users")
        return competition.start_at <= timezone.now() and (
            (eligible_users is None or user_competition_pk in eligible_users)
        )
