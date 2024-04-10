from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
    IngredientViewSet,
    FollowingViewSet
)



router = DefaultRouter()
router.register(r"users/subscriptions", FollowingViewSet, basename="subscriptions")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"users", UserViewSet, basename="users")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(
    r"users/(?P<user_id>\d+)/subscribe", FollowingViewSet, basename="subscribes"
)


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
