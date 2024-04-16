from django_filters.rest_framework import FilterSet
from django_filters import rest_framework

from recipes.models import Ingredient, Recipe


class RecipeFilter(rest_framework.FilterSet):

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset

    is_favorited = rest_framework.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart', )
    tags = rest_framework.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = [
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags',
        ]


class IngredientFilter(FilterSet):
    name = rest_framework.CharFilter(field_name="name",
                                     lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name", )
