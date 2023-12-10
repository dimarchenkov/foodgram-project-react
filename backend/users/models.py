"""
Модуль управления пользователями.
"""
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Q, F

from foodgram_backend import constants


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email, username, password, **extra_fields
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    """
    Модель пользователя.

    Атрибуты:
    ---------
    first_name : str
        Имя пользователя.
    last_name : str
        фамилия пользователя.
    username : str
        Имя пользователя для входа.
    email : str
        Адрес электронной почты пользователя.
    пароль : str
        Пароль пользователя.

    Мета:
    -----
        verbose_name (str): удобочитаемое имя модели.
        порядок (список): порядок модели по умолчанию.

    Методы:
    -------
    __str__(): возвращает имя пользователя в виде строки.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyUserManager()

    first_name = models.CharField(
        max_length=constants.FIRST_NAME_MAX_LENGTH,
        verbose_name='Имя',
        help_text='Введите имя пользователя'
    )
    last_name = models.CharField(
        max_length=constants.LAST_NAME_MAX_LENGTH,
        verbose_name='Фамилия',
        help_text='Введите фамилию пользователя'
    )
    username = models.CharField(
        max_length=constants.USERNAME_MAX_LENGTH,
        unique=True,
        verbose_name='Логин',
        help_text='Введите логин пользователя',
        validators=[
            UnicodeUsernameValidator()
        ],
    )
    email = models.EmailField(
        unique=True,
        verbose_name='E-mail',
        help_text='Введите email пользователя'
    )
    password = models.CharField(
        max_length=constants.PASSWORD_MAX_LENGTH,
        verbose_name='Пароль',
        help_text='Введите пароль пользователя',
        validators=[
            UnicodeUsernameValidator()
        ],
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        """Класс Meta модели User."""
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """
    Представляет подписку между подписчиком и автором.
    Модель M2M.

    Атрибуты:
    ---------
    user : CustomUser
        Пользователь-подписчик.
    автор : CustomUser
        Пользователь-автор.

    Мета:
    -----
    verbose_name (str): удобочитаемое имя модели.
    порядок (список): порядок модели по умолчанию.
    ограничения (список): ограничения модели.

    Методы:
    -------
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
                name='unique_subscription_fields',
                violation_error_message=(
                    {'subscription': 'Уже подписан.'}
                )
            ),
            models.CheckConstraint(
                check=~Q(user=F('following')),
                name='self_subscription',
                violation_error_message=(
                    {'subscription': 'Нельзя подписаться на себя.'}
                )
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
