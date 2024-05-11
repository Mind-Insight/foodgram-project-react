from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model

from users.models import Following
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingList,
)
from .validators import (
    check_following,
    ingredients_validator,
    tags_validator,
    valid_username,
)
from .fields import Base64ImageField

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        valid_username(data)
        if User.objects.filter(username=data.get("username")):
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует"
            )
        if User.objects.filter(email=data.get("email")):
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует"
            )
        return data


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def validate(self, data):
        valid_username(data)
        check_following(data)
        return data

    def get_is_subscribed(self, instance):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return request.user.following.filter(author=instance).exists()


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
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
            "name",
            "measurement_unit",
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadField(source="recipe", many=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_list.filter(recipe=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteField(many=True, write_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("author",)
        validators = [ingredients_validator, tags_validator]

    def validate(self, data):
        ingredients_data = data.get("ingredients")
        all_ingredient_ids = set(
            ingredient_data["ingredient"]
            for ingredient_data in ingredients_data
        )
        all_ingredients = Ingredient.objects.filter(
            id__in=all_ingredient_ids
        )
        if len(all_ingredient_ids) != all_ingredients.count():
            raise serializers.ValidationError(
                "Ингредиент не существует"
            )
        return data

    def create_recipe_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                recipe=recipe,
                amount=ingredient.get('amount'),
            ) for ingredient in ingredients_data]
        )
        # all_ingredients = Ingredient.objects.filter(
        #     id__in=[
        #         ingredient_data["ingredient"]
        #         for ingredient_data in ingredients_data
        #     ]
        # )
        # recipe_ingredients = [
        #     RecipeIngredient(
        #         recipe=recipe,
        #         ingredient=all_ingredients.get(
        #             id=ingredient_data["ingredient"]
        #         ),
        #         amount=ingredient_data["amount"],
        #     )
        #     for ingredient_data in ingredients_data
        # ]
        # RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.get("tags")
        ingredients_data = validated_data.get("ingredients")
        self.create_recipe_ingredients(instance, ingredients_data)
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data


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
    class Meta:
        model = Following
        fields = (
            "user",
            "author",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Following.objects.all(),
                fields=(
                    "user",
                    "author",
                ),
                message="Вы подписаны на этого пользователя",
            ),
        ]

    def validate(self, attrs):
        return check_following(attrs)


class SubscriptionsSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes_limit = self.context["request"].GET.get("recipes_limit")
        recipe_author = obj.recipes.all()
        if recipes_limit is not None:
            recipe_author = obj.recipes.all()[: int(recipes_limit)]
        info_recipe = RecipeSerializerCheck(recipe_author, many=True)
        return info_recipe.data

    def get_recipes_count(self, object):
        return object.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=(
                    "user",
                    "recipe",
                ),
                message="Рецепт уже добавлен в избранное",
            )
        ]


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = (
            "user",
            "recipe",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже добавлен в корзину",
            )
        ]
