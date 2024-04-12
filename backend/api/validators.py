from rest_framework.serializers import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from users.models import Following
from recipes.models import Recipe

User = get_user_model()


def IngredientsValidator(attrs):
    ingredients = attrs.get("ingredients", [])
    if not ingredients:
        raise ValidationError("Должен присутствовать хотя бы один ингредиент.")
    was = set()
    for ingredient in ingredients:
        iid = ingredient.get("ingredient")
        if iid in was:
            raise ValidationError("Ингредиенты должны быть уникальными.")
        was.add(iid)


def TagsValidator(attrs):
    tags = attrs.get("tags", [])
    if not tags:
        raise ValidationError("Должен присутствовать хотя бы один тег.")
    was = set()
    for tag in tags:
        if tag in was:
            raise ValidationError("Теги должны быть уникальными.")
        was.add(tag)


def CheckRecipe(request):
    recipe_id = request.parser_context["kwargs"].get("recipe_id")
    recipe = Recipe.objects.filter(id=recipe_id).first()
    if not recipe:
        raise ValidationError(
            "Вы можете добавлять в избранное только существующие рецепты"
        )
    return recipe


def CheckFollowing(attrs):
    if attrs.get("user") == attrs.get("author"):
        raise serializers.ValidationError("Вы уже подписаны на этого пользователя")
    return attrs
