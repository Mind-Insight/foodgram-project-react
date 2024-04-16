from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .fields import Base64ImageField
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    User,
    RecipeIngredient,
    ShoppingList,
    Favorite,
)
from .validators import ingredients_validator, tags_validator
from users.models import Following


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(following=obj).exists()


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True, source='recipe')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_list.filter(recipe=obj).exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=1,
        max_value=64,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientWriteField(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient")

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )


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
        read_only_fields = ("author", )
        validators = [ingredients_validator, tags_validator]

    def validate(self, data):
        ingredients_data = data.get("ingredients")
        all_ingredient_ids = set(ingredient_data["ingredient"]
                                 for ingredient_data in ingredients_data)
        all_ingredients = Ingredient.objects.filter(id__in=all_ingredient_ids)
        if len(all_ingredient_ids) != all_ingredients.count():
            raise serializers.ValidationError("Ингредиент не существует")
        return data

    def create_recipe_ingredients(self, recipe, ingredients_data):
        all_ingredients = Ingredient.objects.filter(id__in=[
            ingredient_data["ingredient"]
            for ingredient_data in ingredients_data
        ])
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=all_ingredients.get(
                    id=ingredient_data["ingredient"]),
                amount=ingredient_data["amount"],
            ) for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        self.create_recipe_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags_data)
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


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(queryset=ShoppingList.objects.all(),
                                    fields=('user', 'recipe'),
                                    message='Рецепт уже добавлен!')
        ]


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(queryset=Favorite.objects.all(),
                                    fields=('user', 'recipe'),
                                    message='Рецепт уже добавлен!')
        ]


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Following
        fields = (
            'user',
            'following',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Following.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны!!!',
            )
        ]

    def validate(self, data):
        if data.get('user') == data.get('following'):
            raise serializers.ValidationError('Нельзя подписаться на себя!!!')
        return data


class SubscriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        recipe_author = obj.recipe.all()
        if recipes_limit is not None:
            recipe_author = obj.recipe.all()[:int(recipes_limit)]
        info_recipe = RecipeInfoSerializer(recipe_author, many=True)
        return info_recipe.data

    def get_recipes_count(self, obj):
        return obj.recipe.count()
