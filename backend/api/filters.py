from django_filters.rest_framework import FilterSet
from django_filters import rest_framework
from django_filters.widgets import BooleanWidget

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.NumberFilter(
        field_name='author__id',
    )
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = rest_framework.BooleanFilter(
        method='filter_is_favorited',
        widget=BooleanWidget(),
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart',
        widget=BooleanWidget(),
    )

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
        ]

    def filter_is_favorited(
            self, queryset, name: str, value: bool
    ):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite=True)
        return queryset

    def filter_is_in_shopping_cart(
            self, queryset, name: str, value: bool
    ):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list=True)
        return queryset



class IngredientFilter(FilterSet):
    name = rest_framework.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)
