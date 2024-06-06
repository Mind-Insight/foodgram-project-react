from django.db.models import Exists, OuterRef, Count
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models.aggregates import Sum
from djoser.views import UserViewSet
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from users.models import Following
from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    ShoppingList,
)
from .serializers import (
    UserSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    FollowingSerializer,
    FavoriteSerializer,
    ShoppingListSerializer,
    RecipeSerializerCheck,
    SubscriptionsSerializer,
)
from .filters import IngredientFilter, RecipeFilter
from .utils import get_pdf
from .permissions import IsAuthorOrReadOnly
from .paginators import CustomPaginator

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    def get_queryset(self):
        return User.objects.all()

    @action(
        ["GET"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(data=serializer.data)

    @action(
        ["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(serf, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            serializer = FollowingSerializer(
                data={"user": request.user.id, "author": author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            subscriptions_info = SubscriptionsSerializer(
                author,
                context={"request": request},
            )
            return Response(
                data=subscriptions_info.data,
                status=status.HTTP_201_CREATED,
            )
        try:
            follow = Following.objects.get(user=request.user, author=author)
        except Following.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ["GET"],
        detail=False,
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following__user=request.user.id)
        limit = self.request.GET.get("limit")
        if limit is not None:
            subscriptions = User.objects.filter(
                following__user=request.user.id
            )[:int(limit)]
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={"request": request},
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializer(
            subscriptions,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ["get", "post", "delete", "patch"]
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeReadSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
        )

    def add_obj(self, serializer_class, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = serializer_class(
            data={"user": request.user.id, "recipe": recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        recipe_serializer = RecipeSerializerCheck(recipe)
        return Response(
            data=recipe_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def remove_obj(self, model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            item = model.objects.get(user=request.user, **{"recipe": recipe})
        except model.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ["POST", "DELETE"],
        detail=True,
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            return self.add_obj(FavoriteSerializer, request, pk)
        return self.remove_obj(Favorite, request, pk)

    @action(
        ["POST", "DELETE"],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return self.add_obj(ShoppingListSerializer, request, pk)
        return self.remove_obj(ShoppingList, request, pk)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    search_fields = ("name",)
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = IngredientFilter


class FollowingViewSet(viewsets.ModelViewSet):
    serializer_class = FollowingSerializer
    http_method_names = ["get", "post", "delete"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Following.objects.filter(user=self.request.user).annotate(
            is_subscribed=Exists(
                queryset=Following.objects.filter(
                    user=self.request.user, author=OuterRef("pk")
                )
            ),
            recipes_count=Count("author__recipes"),
        )

    def get_following(self):
        return get_object_or_404(User, id=self.kwargs.get("user_id"))

    def get_object(self):
        return get_object_or_404(
            Following.objects,
            user=self.request.user,
            author=self.get_following(),
        )


class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingList.objects.select_related("user", "recipe")
    serializer_class = ShoppingListSerializer
    http_method_names = ["get", "post", "delete"]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "id"

    def get_recipe(self):
        return get_object_or_404(Recipe, id=self.kwargs.get("id"))

    def get_object(self):
        return get_object_or_404(
            self.queryset.model.objects,
            user=self.request.user,
            recipe=self.get_recipe(),
        )

    @action(
        ["GET"],
        detail=False,
    )
    def download_shopping_cart(self, request):
        ingredient_list = (
            ShoppingList.objects.filter(user=request.user)
            .values(
                "recipe__ingredients__name",
                "recipe__ingredients__measurement_unit",
            )
            .annotate(total_amount=Sum("recipe__recipe__amount"))
            .order_by("recipe__ingredients__name")
        )
        return get_pdf(ingredient_list)
