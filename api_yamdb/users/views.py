from django.contrib.auth import get_user_model
from django.http.request import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .serializers import AdminSerializer, SignUpSerializer, UserSerializer
from .utils import send_confirmation_code

User = get_user_model()


class CreateViewSet(CreateModelMixin, GenericViewSet):
    pass


class APIToken(APIView):
    """View-класс для работы с токеном доступа."""
    permission_classes = (AllowAny,)

    def post(self, request):
        """Обработка POST-запросов."""
        try:
            username = request.data['username']
        except KeyError:
            message = {'username': 'Отсутствует username!'}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != request.data['confirmation_code']:
            message = {'confirmation_code': 'Неверный код подтверждения'}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        data = {'token': str(refresh.access_token)}
        return Response(data, status.HTTP_200_OK)


class APIUser(APIView):
    """View-класс для просмотра и редактирования собственного профиля."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Обработка GET-запросов."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request):
        """Обработка PATCH-запросов."""
        serializer = UserSerializer(
            request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)


class SignUpViewSet(CreateViewSet):
    """ViewSet для регистрации и выдачи кода подтверждения."""
    serializer_class = SignUpSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """Проверка на наличие регистрации пользователя
        и отправка кода подтверждения."""
        data = request.data
        if isinstance(data, QueryDict):
            data = data.dict()
        user = User.objects.filter(**data).first()
        if not user:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            user = User.objects.filter(**data).first()
        send_confirmation_code(user)
        return Response(data, status.HTTP_200_OK)


class AdminViewSet(ModelViewSet):
    """ViewSet для работы администратора с моделями пользователей."""
    serializer_class = AdminSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')
