"""
Модуль управления пользователями.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
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
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя',
        help_text='Введите имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия',
        help_text='Введите фамилию пользователя'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Логин',
        help_text='Введите логин пользователя',
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        help_text='Введите email пользователя'
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Пароль',
        help_text='Введите пароль пользователя',
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )

    class Meta:
        """Класс Meta модели User."""
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

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
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Кто подписан на автора'
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='На кого подписан автор',
    )

    class Meta:
        """Класс Meta модели Subscription."""
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
