import sha3

from authentication.models import UserProfile

from ..models import Season, XPRecord


class Context:
    def __init__(self, name, xp, is_global=False, is_onetime=False) -> None:
        self.name = name
        self.xp = xp
        self.is_onetime = True if is_global or is_onetime else False
        self.is_global = True if is_global else False

    def __str__(self):
        return f"{self.name}"


def calculate_event_hash(ctx: Context, pk):
    event = f"{ctx.name}-{pk}"
    hash = sha3.keccak_256()
    hash.update(bytes(event, "utf8"))
    return hash.hexdigest()


def record_xp(user: UserProfile, ctx: Context):
    if ctx.is_global:
        assert not XPRecord.objects.filter(
            context=ctx, user=user
        ).exists(), "XP is already recorded"
    elif ctx.is_onetime:
        try:
            current_season = Season.objects.get(status=Season.Status.ACTIVE)
            assert not XPRecord.objects.filter(
                context=ctx, season=current_season, user=user
            ).exists(), "XP is already recorded"
        except Season.DoesNotExist:
            pass

    new_record = XPRecord.objects.create(
        context=ctx.name, xp=ctx.xp, season=current_season, user=user
    )
    return new_record.save()
