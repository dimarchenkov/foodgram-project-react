"""
Настойки интерфейса панели администратора.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser, Subscription


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class SubscriptionOnInline(admin.StackedInline):
    model = Subscription
    fk_name = 'user'


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    fk_name = 'following'


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Регистрация юзера."""
    model = CustomUser
    add_form = UserCreationForm

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
