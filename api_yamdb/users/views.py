from django.contrib.auth import get_user_model
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
    permission_classes = (AllowAny,)

    def post(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        if not user.confirmation_code or user.confirmation_code != request.data['confirmation_code']:
            message = {'confirmation_code': 'Неверный код подтверждения'}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        data = {'token': str(refresh.access_token)}
        return Response(data, status.HTTP_200_OK)


class APIUser(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)


class SignUpViewSet(CreateViewSet):
    serializer_class = SignUpSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = User.objects.filter(**data).first()
        if not user:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            user = User.objects.filter(**data).first()
        send_confirmation_code(user)
        return Response(data, status.HTTP_200_OK)


class AdminViewSet(ModelViewSet):
    serializer_class = AdminSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')
