"""
Настойки интерфейса панели администратора.
"""
from django.contrib import admin

from .models import CustomUser, Subscription


class SubscriptionOnInline(admin.StackedInline):
    model = Subscription
    fk_name = 'user'


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    fk_name = 'following'


@admin.register(CustomUser)
class Admin(admin.ModelAdmin):
    """Регистрация юзера."""
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff'
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
