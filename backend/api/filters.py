from django_filters.rest_framework import FilterSet
from django_filters import rest_framework

from recipes.models import Recipe, Tag, Ingredient


class RecipeFilter(FilterSet):
    author = rest_framework.NumberFilter(
        field_name="author__id",
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_favorited = rest_framework.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method="filter_is_in_shopping_cart",
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            "author",
            "tags",
        )


class IngredientFilter(FilterSet):
    name = rest_framework.CharFilter(
        field_name="name",
        lookup_expr="istartswith",
    )

    class Meta:
        model = Ingredient
        fields = ("name",)
