from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class TitleGenre(admin.ModelAdmin):
    model = Title


admin.site.register([Category, Comment, Genre, Review])
admin.site.register(Title, TitleGenre)
