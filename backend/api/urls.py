from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    TagViewSet,
    CustomUserViewSet,
    IngredientViewSet,
    ShoppingListViewSet,
)


router = DefaultRouter()
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"users", CustomUserViewSet, basename="users")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")


urlpatterns = [
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
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
