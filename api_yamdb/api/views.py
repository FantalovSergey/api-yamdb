from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework import mixins, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from django.db.models import Avg

from . import serializers
from .permissions import IsAuthorOrModeratorOrReadOnly, IsAdminOrReadOnly
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class CreateViewSet(mixins.CreateModelMixin, GenericViewSet):
    pass


class APIToken(APIView):
    """View-класс для работы с токеном доступа."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Обработка POST-запросов."""
        serializer = serializers.TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status.HTTP_200_OK)


class SignUpViewSet(CreateViewSet):
    """ViewSet для регистрации и выдачи кода подтверждения."""
    serializer_class = serializers.SignUpSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Сериализация данных и отправка ответа с требуемым статус-кодом."""
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(data, status.HTTP_200_OK)


class AdminViewSet(ModelViewSet):
    """ViewSet для работы администратора с моделями пользователей."""
    serializer_class = serializers.AdminSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Обработка запроса пользователя на работу с собственным профилем."""
        if request.method == 'GET':
            serializer = serializers.UserSerializer(request.user)
            return Response(serializer.data, status.HTTP_200_OK)
        serializer = serializers.UserSerializer(
            request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Review."""
    serializer_class = serializers.ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrReadOnly)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        """Получение произведения."""
        try:
            return Title.objects.get(id=self.kwargs.get('title_id'))
        except Title.DoesNotExist:
            raise NotFound('Произведение с указанным ID не существует.')

    def get_queryset(self):
        """Получение queryset для отзывов конкретного произведения."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Создание отзыва с автоматическим указанием автора."""
        title = self.get_title()
        serializer.save(author=self.request.user, title_id=title.id)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Comment."""
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrReadOnly)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        """Получение отзыва, к которому относится(-ятся) комментарий(-и)."""
        try:
            return Review.objects.get(id=self.kwargs.get('review_id'),
                                      title__id=self.kwargs.get('title_id'))
        except Review.DoesNotExist:
            raise NotFound(
                'Отзыв или(и) произведение с указанными ID не существуют.')

    def get_queryset(self):
        """Получение queryset для комментариев конкретного отзыва."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Создание комментария с автоматическим указанием автора."""
        review = self.get_review()
        serializer.save(author=self.request.user, review_id=review.id)


class CategoryGenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Базовый ViewSet для моделей Category и Genre."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreViewSet):
    """ViewSet для модели Category."""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    """ViewSet для модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleFilter(filters.FilterSet):
    """Фильтр для TitleViewSet."""
    category = filters.Filter(field_name='category__slug')
    genre = filters.Filter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('name', 'year')


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Title."""
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')).order_by('-year', 'id')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = TitleFilter
    search_fields = ('name',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        """Получение сериалайзера в зависимости от типа запроса."""
        if self.action in ('list', 'retrieve'):
            return serializers.TitleReadSerializer
        return serializers.TitleWriteSerializer
