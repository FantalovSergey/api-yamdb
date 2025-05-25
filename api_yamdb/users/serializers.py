from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериалайзер для регистрации."""
    class Meta:
        model = User
        fields = ('email', 'username')


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра и редактирования собственного профиля."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class AdminSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра и редактирования профиля администратором."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
