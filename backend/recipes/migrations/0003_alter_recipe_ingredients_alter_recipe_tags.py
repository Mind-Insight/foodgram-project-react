# Generated by Django 5.0.4 on 2024-04-11 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_favorite_options_alter_shoppinglist_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.RecipeIngredient', to='recipes.ingredient'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.tag'),
        ),
    ]
