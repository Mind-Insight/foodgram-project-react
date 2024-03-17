from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from users.models import Following
from recipes.models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
    Tag,
    Favorite,
    ShoppingList,
)
from .serializers import (
    UserRegistrationSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
)

User = get_user_model()


class UserRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = UserRegistrationSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return RecipeReadSerializer
        else:
            return RecipeSerializer

    def get_recipe(self):
        return Recipe.objects.get(pk=self.kwargs.get("pk"))

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
