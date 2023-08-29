""" Настойки интерфейса панели администратора"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, register
from .models import User


@register(User)
class Admin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email')
    empty_value_display = '-empty-'


admin.site.register(User, Admin)
