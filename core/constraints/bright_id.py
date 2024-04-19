from core.constraints.abstract import ConstraintApp, ConstraintVerification


class BrightIDMeetVerification(ConstraintVerification):
    app_name = ConstraintApp.BRIGHT_ID.value

    def is_observed(self, *args, **kwargs):
        return self.user_profile.is_meet_verified


class BrightIDAuraVerification(ConstraintVerification):
    app_name = ConstraintApp.BRIGHT_ID.value

    def is_observed(self, *args, **kwargs):
        return self.user_profile.is_aura_verified
