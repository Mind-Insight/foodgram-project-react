from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from recipes.management.commands import import_ingredients

from .views import (
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
    IngredientViewSet,
    FollowingViewSet,
    FavoriteViewSet,
    ShoppingListViewSet,
)


router = DefaultRouter()
# router.register(
#     r"users/(?P<user_id>\d+)/subscribe",
#     FollowingViewSet,
#     basename="subscribes",
# )
# router.register(
#     r"recipes/(?P<recipe_id>\d+)/shopping_cart",
#     ShoppingListViewSet,
#     basename="shopping_lists",
# )
router.register(r"users/subscriptions", FollowingViewSet, basename="subscriptions")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"users", UserViewSet, basename="users")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
# router.register(
#     r"recipes/(?P<recipe_id>\d+)/favorite",
#     FavoriteViewSet,
#     basename="favorites",
# )


urlpatterns = [
    path(
        "recipes/<int:recipe_id>/favorite/",
        FavoriteViewSet.as_view(
            {
                "post": "create",
                "delete": "destroy",
            },
        ),
    ),
    path(
        "users/<int:user_id>/subscribe/",
        FollowingViewSet.as_view(
            {
                "post": "create",
                "delete": "destroy",
            },
        ),
    ),
    path(
        "recipes/<int:recipe_id>/shopping_cart/",
        ShoppingListViewSet.as_view(
            {
                "delete": "destroy",
                "post": "create",
            },
        ),
    ),
    path(
        "recipes/download_shopping_cart/",
        ShoppingListViewSet.as_view(
            {
                "get": "download_shopping_cart",
            },
        ),
    ),
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
