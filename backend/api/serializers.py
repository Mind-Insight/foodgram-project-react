import webcolors

from base64 import b64decode
from rest_framework import serializers
from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from django.core.files.base import ContentFile

from users.models import Following
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite
from .mixins import RecipeSerializerMixin

from .validators import CheckFollowing

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
    image = Base64ImageField()
    author = UserSerializer(read_only=True)


class RecipeSerializer(RecipeSerializerMixin):
    ingredients = RecipeIngredientWriteField(many=True, write_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    def validate(self, data):
        if self.context["request"].method in ["POST", "PATCH"]:
            if (
                self.instance is not None
                and self.instance.author != self.context["request"].user
            ):
                raise PermissionDenied("Вы не можете обновлять чужой рецепт.")
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        all_id = set(
            ingredient_data["ingredient"] for ingredient_data in ingredients_data
        )
        all_ingredients = Ingredient.objects.filter(id__in=all_id)
        if not all_ingredients:
            raise serializers.ValidationError("err")
        recipe = Recipe.objects.create(**validated_data)
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=all_ingredients.get(id=ingredient_data["ingredient"]),
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.get("tags")
        ingredients_data = validated_data.get("ingredients")
        all_ingredients = Ingredient.objects.all().filter(
            id__in=[ingredient.get("ingredient") for ingredient in ingredients_data]
        )
        if not all_ingredients:
            raise serializers.ValidationError("Ингредиенты пустые.")
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=all_ingredients.get(id=ingredient.get("ingredient")),
                    amount=ingredient.get("amount"),
                )
                for ingredient in ingredients_data
            ]
        )
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance)
        return serializer.data


class RecipeSerializerCheck(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FollowingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="author.id", read_only=True)
    username = serializers.CharField(source="author.username", read_only=True)
    first_name = serializers.CharField(source="author.first_name", read_only=True)
    last_name = serializers.CharField(source="author.last_name", read_only=True)
    email = serializers.EmailField(source="author.email", read_only=True)
    recipes = RecipeSerializerCheck(source="author.recipes", many=True, read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)
    is_subscribed = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Following
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "recipes",
            "recipes_count",
            "is_subscribed",
        )

    def validate(self, attrs):
        return CheckFollowing(attrs, self.context["request"], self.context["view"])

    def create(self, validated_data):
        return Following.objects.create(
            user=validated_data["user"], author=validated_data["author"]
        )

    def to_representation(self, instance):
        if self.context["request"].method == "POST":
            instance = self.context["view"].get_queryset().get(id=instance.id)
        data = super().to_representation(instance)
        recipes_limit = self.context["request"].query_params.get("recipes_limit")
        recipes = data["recipes"]
        if recipes_limit and recipes and len(recipes) > int(recipes_limit):
            data["recipes"] = recipes[: int(recipes_limit)]
        return data


# class FavoriteSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = Favor