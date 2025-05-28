from django_filters.rest_framework import Filter, FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    """Фильтр для TitleViewSet."""
    category = Filter(field_name='category__slug', lookup_expr='icontains')
    genre = Filter(field_name='genre__slug', lookup_expr='icontains')
    name = Filter(lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')
