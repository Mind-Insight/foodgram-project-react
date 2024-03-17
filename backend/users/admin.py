from django.contrib.auth.admin import UserAdmin
from .models import FoodgramUser
from django.contrib import admin


class FoodgramUserAdmin(UserAdmin):
    model = FoodgramUser
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {"fields": ("role",)},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {"fields": ("role",)},
        ),
    )
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
    )


admin.site.register(FoodgramUser, FoodgramUserAdmin)
