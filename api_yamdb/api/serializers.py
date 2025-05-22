from rest_framework import serializers
from reviews.models import Category, Genre, Title, Review, Comment


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

    class Meta:
        model = Title
        fields = '__all__'


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author_id', 'score', 'pub_date')
        read_only_fields = ('author_id',)

    def validate(self, data):
        """Проверка на уникальность отзыва."""
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            author_id = self.context['request'].user.id
            if Review.objects.filter(
                title_id=title_id,
                author_id=author_id
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author_id', 'pub_date')
        read_only_fields = ('author_id',)
