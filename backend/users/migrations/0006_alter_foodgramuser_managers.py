# Generated by Django 5.0.4 on 2024-04-09 14:09

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_foodgramuser_role'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='foodgramuser',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]