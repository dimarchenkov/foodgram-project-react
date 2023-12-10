"""
Настойки интерфейса панели администратора.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import CustomUser, Subscription


class SubscriptionOnInline(admin.StackedInline):
    model = Subscription
    fk_name = 'user'


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    fk_name = 'following'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Регистрация юзера."""
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
    )
    list_filter = (
        'email',
        'username',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    inlines = [SubscriptionOnInline, SubscriptionInline]

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions'
        )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Contact info', {'fields': ('contact_no',)}),)


@admin.register(Subscription)
class FollowAdmin(admin.ModelAdmin):
    """Регистрация подписчика."""
    list_display = (
        'user',
        'following',
    )
    search_fields = (
        'user',
        'following',
    )


admin.site.site_header = 'Администрирование Foodgram'
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
