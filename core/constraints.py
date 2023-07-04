from authentication.models import UserProfile

class BrightIDMeetVerification():
    def is_passed(self, user_profile: UserProfile, *args, **kwargs):
        return user_profile.is_meet_verified

    def response(self):
        return "You must be verified on BrightID"


class BrightIDAuraVerification():
    def is_passed(self, user_profile: UserProfile, *args, **kwargs):
        return user_profile.is_aura_verified

    def response(self):
        return "You must be Aura verified on BrightID"
    