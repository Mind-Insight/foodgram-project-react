# Generated by Django 5.0.4 on 2024-04-08 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0003_alter_foodgramuser_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foodgramuser',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AddIndex(
            model_name='foodgramuser',
            index=models.Index(fields=['first_name', 'last_name'], name='user_index_fields'),
        ),
    ]
