from rest_framework.permissions import BasePermission


class AllowAnyForNowPermission(BasePermission):
    """
    Placeholder permission to keep the first API iteration simple.

    Replace this with role-based access once the core workflow is stable.
    """

    def has_permission(self, request, view) -> bool:
        return True
