from djoser.views import UserViewSet
from django.db.models.aggregates import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    ShoppingList,
    Favorite,
    User,
)
from users.models import Following
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthor
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    ShoppingListSerializer,
    RecipeInfoSerializer,
    FavoriteSerializer,
    UserSerializer,
    FollowSerializer,
    SubscriptionsSerializer,
)
from .utils import get_pdf


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'delete', 'patch']

    @action(
        ['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(data=serializer.data)

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(serf, request, id):
        following = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(data={
                'user': request.user.id,
                'following': following.id
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            subscriptions_info = SubscriptionsSerializer(
                following,
                context={'request': request},
            )
            return Response(
                data=subscriptions_info.data,
                status=status.HTTP_201_CREATED,
            )
        try:
            follow = Following.objects.get(user=request.user,
                                           following=following)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['GET'],
        detail=False,
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following__user=request.user.id)
        limit = self.request.GET.get('limit')
        if limit is not None:
            subscriptions = User.objects.filter(
                following__user=request.user.id)[:int(limit)]
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={'request': request},
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializer(
            subscriptions,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    search_fields = ('name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'delete', 'patch']
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthor)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeReadSerializer
        return RecipeSerializer

    def add_obj(self, serializer_class, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = serializer_class(data={
            'user': request.user.id,
            'recipe': recipe.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        recipe_serializer = RecipeInfoSerializer(recipe)
        return Response(
            data=recipe_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def remove_obj(self, model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            item = model.objects.get(user=request.user, **{'recipe': recipe})
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['POST', 'DELETE'],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(ShoppingListSerializer, request, pk)
        return self.remove_obj(ShoppingList, request, pk)

    @action(
        ['POST', 'DELETE'],
        detail=True,
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(FavoriteSerializer, request, pk)
        return self.remove_obj(Favorite, request, pk)

    @action(
        ['GET'],
        detail=False,
    )
    def download_shopping_cart(self, request):
        ingredient_list = ShoppingList.objects.filter(
            user=request.user).values(
                'recipe__ingredients__name',
                'recipe__ingredients__measurement_unit',
            ).annotate(total_amount=Sum('recipe__recipe__amount')).order_by(
                'recipe__ingredients__name')
        return get_pdf(ingredient_list)
