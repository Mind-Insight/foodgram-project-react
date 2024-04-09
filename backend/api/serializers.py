import webcolors

from base64 import b64decode
from rest_framework import serializers
from djoser.serializers import UserSerializer
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


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(read_only=True, default=False)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("is_subscribed",)


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
            "name",
            "measurement_unit",
        )


class RecipeIngredientWriteField(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient")

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )


class RecipeIngredientReadField(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
            "name",
            "measurement_unit",
        )


class RecipeReadSerializer(RecipeSerializerMixin):
    ingredients = RecipeIngredientReadField(source="recipeingredient_set", many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(allow_null=True)
    author = UserSerializer(read_only=True)


class RecipeSerializer(RecipeSerializerMixin):
    ingredients = RecipeIngredientWriteField(many=True, write_only=True)
    image = Base64ImageField(allow_null=True)
    author = UserSerializer(read_only=True)

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        available_ids = [
            ingredient_data.get("ingredient") for ingredient_data in ingredients_data
        ]
        ingredients = Ingredient.objects.all().filter(id__in=available_ids)

        for ingredient_data in ingredients_data:
            cur_ingredient = ingredients.get(id=ingredient_data.get("ingredient"))
            amount = ingredient_data.get("amount")
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=cur_ingredient, amount=amount
            )

        for tag in tags:
            recipe.tags.add(tag)

        return recipe

    def to_representation(self, instance):
        if self.context["request"].method in ["POST", "PATCH"]:
            instance = self.context["view"].get_queryset().get(id=instance.id)
        return RecipeReadSerializer(instance=instance, context=self.context).data
