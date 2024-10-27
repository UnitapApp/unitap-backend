from core.constraints.abstract import ConstraintApp, ConstraintVerification


class HasENSVerification(ConstraintVerification):
    _param_keys = []
    app_name = ConstraintApp.ENS.value

    def is_observed(self, *args, **kwargs) -> bool:
        from authentication.models import ENSConnection

        try:
            ens = ENSConnection.get_connection(self.user_profile)
        except ENSConnection.DoesNotExist:
            return False
        return ens.is_connected()
