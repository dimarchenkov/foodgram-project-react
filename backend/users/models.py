"""
Модуль управления пользователями.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Логин',
        unique=True,
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='e-mail',
        unique=True,
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        ordering = ['username']
        verbose_name = 'Пользователь'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок пользователей. """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = "Подписка"
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow_model'
            )
        ]

    def __str__(self):
        return self.user.username
