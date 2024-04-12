from django.contrib import admin

from .models import FoodgramUser


@admin.register(FoodgramUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_editable = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    list_per_page = 10
    list_filter = ("email", "username")
