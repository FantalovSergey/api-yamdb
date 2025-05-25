from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from reviews.models import Category, Genre, Title, Review
from .serializers import ReviewSerializer, CommentSerializer
from .permissions import IsAuthorOrModeratorOrReadOnly, IsAdminOrReadOnly

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from reviews.models import Review, Comment, Category, Genre, Title
from .serializers import ReviewSerializer, CommentSerializer
from .permissions import IsAuthorOrModeratorOrReadOnly, IsAdminOrReadOnly

from rest_framework import viewsets, mixins, filters

from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer
)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Review."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        try:
            return Title.objects.get(id=self.kwargs.get('title_id'))
        except Title.DoesNotExist:
            raise NotFound('Произведение с указанным ID не существует!')

    def get_queryset(self):
        """Получение queryset для отзывов конкретного произведения."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Создание отзыва с автоматическим указанием автора."""
        title = self.get_title()
        serializer.save(author=self.request.user, title_id=title.id)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Comment."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        try:
            return Title.objects.get(id=self.kwargs.get('title_id'))
        except Title.DoesNotExist:
            raise NotFound('Произведение с указанным ID не существует!')

    def get_review(self):
        """Получение отзыва, к которому относится(-ятся) комментарий(-и)"""
        title = self.get_title()
        try:
            return title.reviews.get(id=self.kwargs.get('review_id'))
        except Review.DoesNotExist:
            raise NotFound('Отзыв с указанным ID не существует')

    def get_queryset(self):
        """Получение queryset для комментариев конкретного отзыва."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Создание комментария с автоматическим указанием автора."""
        review = self.get_review()
        serializer.save(author=self.request.user, review_id=review.id)


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer

    def get_queryset(self):
        queryset = self.queryset

        category_slug = self.request.query_params.get('category')
        genre_slug = self.request.query_params.get('genre')
        name = self.request.query_params.get('name')
        year = self.request.query_params.get('year')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if year:
            queryset = queryset.filter(year=year)

        return queryset