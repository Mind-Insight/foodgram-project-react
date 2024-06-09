from rest_framework.serializers import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


def ingredients_validator(attrs):
    ingredients = attrs.get("ingredients", [])
    if not ingredients:
        raise ValidationError("Должен присутствовать хотя бы один ингредиент.")
    unique_ingredients_ids = set()
    for ingredient in ingredients:
        ingredient_id = ingredient.get("ingredient")
        if ingredient_id in unique_ingredients_ids:
            raise ValidationError("Ингредиенты должны быть уникальными.")


def tags_validator(attrs):
    tags = attrs.get("tags", [])
    if not tags:
        raise ValidationError("Должен присутствовать хотя бы один тег.")
    unique_tags = set()
    for tag in tags:
        if tag in unique_tags:
            raise ValidationError("Теги должны быть уникальными.")
        unique_tags.add(tag)


def check_following(attrs):
    if attrs.get("user") == attrs.get("author"):
        raise serializers.ValidationError("Вы уже подписаны на этого пользователя")
    return attrs


def valid_username(attrs):
    if attrs.get("username") == "me":
        raise serializers.ValidationError("Использовать имя me запрещено")


def validate_user_fields(attrs):
    first_name = attrs.get("first_name")
    last_name = attrs.get("last_name")
    username = attrs.get("username")
    if len(set([first_name, last_name, username])) != 3:
        raise ValidationError(
            "Поля username, name, surname должны "
            "быть уникальными в пределах одной записи"
        )


def validate_exist_user(attrs):
    username = attrs.get("username")
    email = attrs.get("email")
    if User.objects.filter(username=username):
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует"
            )
    if User.objects.filter(email=email):
        raise serializers.ValidationError(
            "Пользователь с таким email уже существует"
        )