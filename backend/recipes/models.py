from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        related_name="recipes",
    )
    title = models.CharField(
        "Название",
        max_length=255,
    )
    image = models.ImageField(
        "Картинка",
        upload_to="recipes/images/",
        default=None,
    )
    description = models.TextField(
        "Описание",
    )
    ingredients = models.ManyToManyField(
        "Ingredient",
        related_name="recipes_ingredient",
        through="RecipeIngredient",
    )
    tags = models.ManyToManyField(
        "Tag",
        related_name="recipe_tags",
    )
    time = models.SmallIntegerField(
        "Время приготовления",
        validators=[
            MinValueValidator(5),
            MaxValueValidator(420),
        ],
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self) -> str:
        return self.title


class Tag(models.Model):
    tag_title = models.CharField(
        "Тег",
        max_length=255,
        unique=True,
    )
    color = models.CharField(
        "Цвет",
        max_length=16,
        unique=True,
    )
    slug = models.SlugField(
        "Слаг",
        unique=True,
    )

    def clean(self):
        if len(set([self.tag_title, self.color, self.slug])) != 3:
            raise ValidationError("Значения всех трех полей должны быть различными.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Ingredient(models.Model):
    title = models.CharField(
        "Ингредиент",
        max_length=255,
    )
    units = models.CharField(
        "Единицы измерения",
        max_length=10,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self) -> str:
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.SmallIntegerField(
        "Количество",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(64),
        ],
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_list",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    added = models.DateTimeField(
        "Время добавления",
        auto_now_add=True,
    )
