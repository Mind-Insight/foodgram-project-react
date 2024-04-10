from rest_framework.serializers import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from users.models import Following

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


def CheckFollowing(attrs, request, view):
    user = request.user
    author = view.get_following()
    if user.id == author.id:
        raise serializers.ValidationError(
            "Вы можете подписываться только на других пользователей."
        )

    if Following.objects.filter(user=user, author=author).exists():
        raise serializers.ValidationError("Данные пользователь уже у вас в подписках")
    attrs["user"] = user
    attrs["author"] = author
    return attrs
