"""Модуль разрешений для api версии 1."""
from rest_framework import permissions


class isAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """
    Пользовательский класс разрешений, который позволяет безопасным методам
    или прошедшим проверку пользователям получать разрешения.

    Методы:
        has_permission(request, view): возвращает True, если метод запроса
        безопасен или пользователь аутентифицирован,
        в противном случае — False.
        has_object_permission(request, view, obj): возвращает True, если метод
        запроса безопасен или пользователь прошел проверку подлинности и имеет
        права администратора, суперпользователя или автора для объекта,
        в противном случае — False.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (
                request.user.is_admin
                or request.user.is_superuser
                or obj.author == request.user
            )
        return False
