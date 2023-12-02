""" Модуль разрешений.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class isAdminOrAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        if request.user and request.user.is_staff:
            return True

        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return (
                obj.author == request.user
            )
        return False
