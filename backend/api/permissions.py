"""
Модуль настройки разрешений.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class isAdminOrAuthorOrReadOnly(BasePermission):
    """
    Checks if the user has permission to perform the requested action.

    For `has_permission`:
        Returns True if the request method is safe (GET, HEAD, OPTIONS)
        or if the user is authenticated or is a staff member.
        Otherwise, returns False.

    Args:
        request: The request object.
        view: The view object.

    Returns:
        bool: True if the user has permission, False otherwise.

    For `has_object_permission`:
        Returns True if the request method is safe (GET, HEAD, OPTIONS)
        or if the user is authenticated and is the author of the object.
        Otherwise, returns False.

    Args:
        request: The request object.
        view: The view object.
        obj: The object being accessed.

    Returns:
        bool: True if the user has permission, False otherwise.
    """
    def has_permission(self, request, view) -> bool:
        """
        Checks if the user has permission to perform the requested action.

        Args:
            self: The instance of the permission class.
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Checks if the user has permission to access the specified object.

        Args:
            self: The instance of the permission class.
            request: The request object.
            view: The view object.
            obj: The object being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and obj.author == request.user
        )
