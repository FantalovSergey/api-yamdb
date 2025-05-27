from django.contrib.auth.models import AbstractUser
from django.db import models

from . import constants
from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""
    class Roles(models.TextChoices):
        USER = ('user', 'U')
        MODERATOR = ('moderator', 'M')
        ADMIN = ('admin', 'A')

    username = models.CharField(
        max_length=constants.CHAR_FIELD_MAX_LENGTH,
        unique=True,
        validators=[validate_username],
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(max_length=constants.EMAIL_FIELD_MAX_LENGTH,
                              unique=True)
    first_name = models.CharField(
        max_length=constants.CHAR_FIELD_MAX_LENGTH,
        blank=True,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=constants.CHAR_FIELD_MAX_LENGTH,
        blank=True,
        verbose_name='Фамилия',
    )
    bio = models.TextField(blank=True, verbose_name='О пользователе')
    role = models.SlugField(
        default=Roles.USER, choices=Roles.choices, verbose_name='Роль')

    class Meta:
        ordering = ('-date_joined', 'id')
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN.value

    @property
    def is_moderator(self):
        return self.role == self.Roles.MODERATOR.value
