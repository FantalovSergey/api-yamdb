import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class Command(BaseCommand):
    help = 'Импортирует данные из CSV-файлов в базу данных через ORM'

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        self.load_users(os.path.join(data_dir, 'users.csv'))
        self.load_categories(os.path.join(data_dir, 'category.csv'))
        self.load_genres(os.path.join(data_dir, 'genre.csv'))
        self.load_titles(os.path.join(data_dir, 'titles.csv'))
        self.load_genre_title(os.path.join(data_dir, 'genre_title.csv'))
        self.load_reviews(os.path.join(data_dir, 'review.csv'))
        self.load_comments(os.path.join(data_dir, 'comments.csv'))

    def load_users(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                User.objects.get_or_create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row.get('role', 'user'),
                    bio=row.get('bio', ''),
                    first_name=row.get('first_name', ''),
                    last_name=row.get('last_name', ''),
                )

    def load_categories(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                Category.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )

    def load_genres(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                Genre.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )

    def load_titles(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                category = Category.objects.get(id=row['category'])
                Title.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=category
                )

    def load_genre_title(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)

    def load_reviews(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                Review.objects.get_or_create(
                    id=row['id'],
                    title=Title.objects.get(id=row['title_id']),
                    text=row['text'],
                    author=User.objects.get(id=row['author']),
                    score=row['score'],
                    pub_date=row['pub_date']
                )

    def load_comments(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                Comment.objects.get_or_create(
                    id=row['id'],
                    review=Review.objects.get(id=row['review_id']),
                    text=row['text'],
                    author=User.objects.get(id=row['author']),
                    pub_date=row['pub_date']
                )