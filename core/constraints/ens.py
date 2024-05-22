from core.constraints.abstract import ConstraintApp, ConstraintVerification


class HasENSVerification(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.ENS.value

    def __init__(self, user_profile) -> None:
        super().__init__(user_profile)

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import ENSConnection

        try:
            ens = ENSConnection.objects.get(user_profile=self.user_profile)
        except ENSConnection.DoesNotExist:
            return False
        return ens.name is not None
