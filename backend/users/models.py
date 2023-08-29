""" Модуль управления пользователями."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User class."""
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин',
        # validators=(UnicodeUsernameValidator(), validate_username,)
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
    )
    email = models.EmailField(
        unique=True,
        verbose_name='e-mail',
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.username)
