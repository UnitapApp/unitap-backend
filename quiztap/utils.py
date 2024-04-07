from django.core.cache import cache
from django.utils import timezone

from authentication.models import UserProfile
from quiztap.models import Competition, UserCompetition


def is_user_eligible_to_participate(
    user_profile: UserProfile, competition: Competition
) -> bool:
    try:
        user_competition_pk = UserCompetition.objects.get(
            user_profile=user_profile, competition=competition
        ).pk
    except UserCompetition.DoesNotExist:
        return False
    eligible_users = cache.get(f"comp_{competition.pk}_eligible_users")
    return (
        competition.is_active
        and competition.status == competition.Status.IN_PROGRESS
        and competition.start_at <= timezone.now()
        and ((eligible_users is None or user_competition_pk in eligible_users))
    )
