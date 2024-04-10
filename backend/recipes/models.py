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
    name = models.CharField(
        "Название",
        max_length=200,
    )
    image = models.ImageField(
        "Картинка",
        upload_to="recipes/",
        default=None,
    )
    text = models.TextField(
        "Описание",
    )
    ingredients = models.ManyToManyField(
        "Ingredient",
        related_name="recipes",
        through="RecipeIngredient",
    )
    tags = models.ManyToManyField(
        "Tag",
        related_name="recipe_tags",
    )
    cooking_time = models.SmallIntegerField(
        "Время приготовления",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(420),
        ],
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
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
        if len(set([self.name, self.color, self.slug])) != 3:
            raise ValidationError("Значения всех трех полей должны быть различными.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        "Ингредиент",
        max_length=255,
    )
    measurement_unit = models.CharField(
        "Единицы измерения",
        max_length=10,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient',
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
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    added = models.DateTimeField(
        "Время добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        default_related_name = 'favorites'
        ordering = ("added",)

    def __str__(self):
        return f"{self.user} добавил в избранное рецепт {self.recipe}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    added = models.DateTimeField(
        "Время добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'КорзинаПокупок'
        verbose_name_plural = 'КорзиныПокупок'
        default_related_name = 'shopping_list'
