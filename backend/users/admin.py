"""
Настойки интерфейса панели администратора.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User


@admin.register(User)
class Admin(UserAdmin):
    """Регистрация юзера."""
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_filter = (
        'email',
        'username',
    )
    search_fields = (
        'username',
        'email',
    )
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Регистрация подписчика."""
    list_display = (
        'user',
        'author',
    )
