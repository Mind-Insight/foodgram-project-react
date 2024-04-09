from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
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
    CustomUserSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
)

User = get_user_model()


class UserViewSet(UserViewSet):

    def get_queryset(self):
        return User.objects.all()

    @action(
        ["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(data=serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ["get", "post", "delete", "patch"]

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
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
