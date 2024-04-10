from django.db.models import Count, OuterRef, Subquery
from django.db.models import F
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from users.models import Following
from recipes.models import (
    Recipe,
    Ingredient,
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
    FollowingSerializer,
)
from .filters import IngredientFilter, RecipeFilter

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
    filterset_class = RecipeFilter

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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    search_field = ("name",)
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class FollowingViewSet(viewsets.ModelViewSet):
    serializer_class = FollowingSerializer
    http_method_names = ["get", "post", "delete"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        author_subquery = (
            Following.objects.filter(user=self.request.user, author=OuterRef("pk"))
            .values("author")
            .annotate(exists=Count("pk"))
            .values("exists")
        )

        return Following.objects.filter(user=self.request.user).annotate(
            is_subscribed=Coalesce(
                Subquery(author_subquery), Value(0), output_field=IntegerField()
            ),
            recipes_count=Coalesce(
                Cast(F("author__recipes"), output_field=IntegerField()), Value(0)
            ),
        )

    def get_following(self):
        return get_object_or_404(User, id=self.kwargs.get("user_id"))

    def get_object(self):
        return get_object_or_404(
            Following.objects, user=self.request.user, author=self.get_following()
        )
