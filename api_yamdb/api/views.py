from rest_framework import filters, mixins, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from reviews.models import Category, Genre, Review, Title
from .permissions import IsAuthorOrModeratorOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer
)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Review."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        """Получение произведения."""
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
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        """Получение произведения."""
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
    """ViewSet для модели Category."""
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
    """ViewSet для модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Title."""
    queryset = Title.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Получение сериалайзера в зависимости от типа запроса."""
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer

    def get_queryset(self):
        """Получение queryset произведений."""
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

    def create(self, request, *args, **kwargs):
        """Создание объекта произведения
        с выводом жанра и категории в качестве объектов в ответе."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = serializer.data
        data['genre'] = [
            Genre.objects.filter(slug=genre).values('name', 'slug')[0]
            for genre in data['genre']
        ]
        data['category'] = Category.objects.filter(
            slug=data['category']).values('name', 'slug')[0]
        return Response(data, status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Обновление объекта произведения
        с выводом жанра и категории в качестве объектов в ответе."""
        serializer = self.get_serializer(
            instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data['genre'] = [
            Genre.objects.filter(slug=genre).values('name', 'slug')[0]
            for genre in data['genre']
        ]
        data['category'] = Category.objects.filter(
            slug=data['category']).values('name', 'slug')[0]
        return Response(data, status.HTTP_200_OK)
