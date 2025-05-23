from rest_framework import serializers
from rest_framework.exceptions import NotFound

from reviews.models import Review, Comment, Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author',)

    def validate(self, data):
        """Проверка на уникальность отзыва и существование title_id."""
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            author = self.context['request'].user.id
            
            # Проверка существования title_id
            try:
                Title.objects.get(pk=title_id)
            except Title.DoesNotExist:
                raise NotFound(
                    'Произведение с указанным ID не существует'
                )
            
            # Проверка на уникальность отзыва
            if Review.objects.filter(
                title_id=title_id,
                author=author
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author',)

    def validate(self, data):
        """Проверка существования review_id."""
        if self.context['request'].method == 'POST':
            review_id = self.context['view'].kwargs.get('review_id')
            try:
                Review.objects.get(pk=review_id)
            except Review.DoesNotExist:
                raise NotFound(
                    'Отзыв с указанным ID не существует'
                )
        return data
