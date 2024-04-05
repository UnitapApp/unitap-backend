from rest_framework.permissions import BasePermission


class IsMeetVerified(BasePermission):
    """
    Allows access only to Meet verified users.
    """

    def has_permission(self, request, view):
        return bool(request.user.profile.is_meet_verified)


class IsAuraVerified(BasePermission):
    """
    Allows access only to Aura verified users.
    """

    def has_permission(self, request, view):
        return bool(request.user.profile.is_aura_verified)


class IsOwner(BasePermission):
    """
    Just owner can access
    """

    def has_object_permission(self, request, view, obj):
        return obj.user_profile == request.user.profile
