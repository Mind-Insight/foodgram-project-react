import webcolors

from base64 import b64decode
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from users.models import Following
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from .mixins import RecipeSerializerMixin

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(b64decode(imgstr), name=f"temp.{ext}")
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("Для данного цвета нет имени")
        return data


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.BooleanField(default=False)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
        )

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "title",
            "measurement_unit",
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="ingredient.title")
    measurement_unit = serializers.CharField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "title",
            "measurement_unit",
            "amount",
        )


class RecipeReadSerializer(RecipeSerializerMixin):
    ingredients = RecipeIngredientSerializer(source="recipeingredient_set", many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(allow_null=True)
    author = UserSerializer()


class RecipeSerializer(RecipeSerializerMixin):
    ingredients = RecipeIngredientSerializer(source="recipeingredient_set", many=True)
    image = Base64ImageField(allow_null=True)
    author = UserSerializer()

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            cur_ingredient, _ = Ingredient.objects.get_or_create(**ingredient)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=cur_ingredient, amount=10
            )
        for tag in tags:
            recipe.tags.add(tag)
        return recipe
