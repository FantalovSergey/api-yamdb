from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""
    ROLE_CHOICES = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+\Z'),
            RegexValidator(
                regex=r'^(?!me$)',
                message=('Запрещено использовать me '
                         'в качестве имени пользователя!')
            )
        ],
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(
        max_length=150, blank=True, default='', verbose_name='Имя')
    last_name = models.CharField(
        max_length=150, blank=True, default='', verbose_name='Фамилия')
    bio = models.TextField(
        blank=True, default='', verbose_name='О пользователе')
    role = models.SlugField(
        default='user', choices=ROLE_CHOICES, verbose_name='Роль')
    confirmation_code = models.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        default='0',
        verbose_name='Код подтверждения',
    )

    class Meta:
        ordering = ('-date_joined',)
