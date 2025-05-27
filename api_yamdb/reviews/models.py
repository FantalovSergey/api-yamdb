from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg

from . import constants

User = get_user_model()


class Review(models.Model):
    """Модель отзыва на произведение."""
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(constants.SCORE_MIN_VALUE),
                    MaxValueValidator(constants.SCORE_MAX_VALUE)],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв {self.author} на {self.title}'


class Comment(models.Model):
    """Модель комментария к отзыву."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Комментарий {self.author} к отзыву {self.review}'


class BaseCategoryGenre(models.Model):
    """Базовый класс для моделей Category и Genre."""
    name = models.CharField(
        max_length=constants.CHAR_FIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Название',
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        ordering = ['slug']

    def __str__(self):
        return self.name


class Category(BaseCategoryGenre):
    """Модель категории."""
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseCategoryGenre):
    """Модель жанра."""
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(max_length=constants.CHAR_FIELD_MAX_LENGTH,
                            verbose_name='Название')
    year = models.IntegerField(
        validators=[MaxValueValidator(datetime.now().year)],
        verbose_name='Год выпуска',
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles', null=True,
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['-year']

    def update_rating(self):
        """Обновление рейтинга произведения."""
        avg_rating = self.reviews.aggregate(Avg('score'))['score__avg']
        self.rating = int(avg_rating) if avg_rating else None
        self.save()

    def __str__(self):
        return self.name
