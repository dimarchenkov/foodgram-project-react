"""
Модуль управления пользователями.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
        Представляет пользователя в системе.

        Атрибуты:
            first_name (str): Имя пользователя.
            Last_name (str): фамилия пользователя.
            username (str): Имя пользователя для входа.
            электронная почта (str): адрес электронной почты пользователя.
            пароль (str): пароль пользователя.

        Мета:
            verbose_name (str): удобочитаемое имя модели.
            порядок (список): порядок модели по умолчанию.

        Методы:
            __str__(): возвращает имя пользователя в виде строки.
    """

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите имя пользователя'
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
        """Класс Meta модели User."""
        verbose_name = 'Пользователь'
        ordering = ['username']
        verbose_name = 'Пользователь'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """
        Представляет подписку между подписчиком и автором.
        Модель M2M.

        Атрибуты:
            user (Пользователь): Пользователь-подписчик.
            автор (Пользователь): Пользователь-автор.

        Мета:
            verbose_name (str): удобочитаемое имя модели.
            порядок (список): порядок модели по умолчанию.
            ограничения (список): ограничения модели.

        Методы:
            __str__(): возвращает строковое представление подписки.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчики автора'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Подписки автора'
    )

    class Meta:
        """Класс Meta модели Subscription."""
        verbose_name = "Подписка"
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user} --> {self.author}'
