from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
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
