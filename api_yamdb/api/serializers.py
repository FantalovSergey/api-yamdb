from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator as token
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title
from users import constants
from users.validators import validate_username

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    """Сериалайзер для регистрации."""
    username = serializers.CharField(
        max_length=constants.CHAR_FIELD_MAX_LENGTH,
        validators=[validate_username],
    )
    email = serializers.EmailField(max_length=constants.EMAIL_FIELD_MAX_LENGTH)

    def validate(self, attrs):
        """Валидация регистрационных данных."""
        username = attrs.get('username')
        user_with_username = User.objects.filter(
            username=username).first()
        user_with_email = User.objects.filter(
            email=attrs.get('email')).first()
        if user_with_username != user_with_email:
            message = {}
            if user_with_username:
                message.update({'username': (
                    'Пользователь с таким username уже существует.')})
            if user_with_email:
                message.update({'email': (
                    'Пользователь с таким email уже существует.')})
            raise serializers.ValidationError(message)
        return attrs

    def create(self, validated_data):
        """Регистрация нового пользователя и отправка кода подтверждения."""
        user, _ = User.objects.get_or_create(**validated_data)
        send_mail(
            subject='Confirmation code',
            message=(f'\t{user.username},\nВаш код подтверждения '
                     f'для получения токена YaMDb: {token.make_token(user)}'),
            from_email=None,
            recipient_list=[user.email],
        )
        return user


class TokenSerializer(serializers.Serializer):
    """"Сериализатор для получения токена доступа."""
    username = serializers.CharField(
        max_length=constants.CHAR_FIELD_MAX_LENGTH)
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        """Валидация данных, отправленных для получения токена доступа."""
        try:
            username = attrs['username']
        except KeyError:
            raise serializers.ValidationError('Отсутствует поле username.')
        user = get_object_or_404(User, username=username)
        if not token.check_token(user, attrs.get('confirmation_code')):
            raise serializers.ValidationError('Неверный код подтверждения.')
        return user

    def to_representation(self, instance):
        """Отправка токена доступа."""
        return {'token': str(AccessToken.for_user(instance))}


class AdminSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра и редактирования профиля администратором."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')


class UserSerializer(AdminSerializer):
    """Сериалайзер для просмотра и редактирования собственного профиля."""
    class Meta(AdminSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Category."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Genre."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Title при безопасных запросах."""
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Title при небезопасных запросах."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        allow_null=False,
        allow_empty=False,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, instance):
        """Вывод жанра и категории в качестве объектов в ответе."""
        serializer = TitleReadSerializer(instance)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Проверка на уникальность отзыва."""
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            author = self.context['request'].user.id
            if Review.objects.filter(
                    title_id=title_id,
                    author=author
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
