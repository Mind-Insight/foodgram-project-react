from django_filters.rest_framework import FilterSet
from django_filters import rest_framework

from recipes.models import Ingredient, Recipe


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.NumberFilter(field_name="author__id")
    tags = rest_framework.CharFilter(method="filter_tags")

    def filter_tags(self, queryset, name, value):
        tags_list = value.split(",")
        return queryset.filter(tags__slug__in=tags_list)

    class Meta:
        model = Recipe
        fields = (
            "author",
            "tags",
        )


class IngredientFilter(FilterSet):
    name = rest_framework.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)
