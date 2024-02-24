from django.contrib.auth.models import AbstractUser
from django.db import models

from constants import GUEST, AUTHORIZED, ADMIN


class FoodgramUser(AbstractUser):

    class Role(models.TextChoices):
        GUEST = GUEST, "гость"
        AUTHORIZED = AUTHORIZED, "авторизованный пользователь"
        ADMIN = ADMIN, "админ"

    email = models.EmailField(
        "Электронная почта",
        max_length=255,
        unique=True,
    )
    name = models.CharField(
        "Имя",
        max_length=100,
    )
    surname = models.CharField(
        "Фамилия",
        max_length=100,
    )
    role = models.CharField(
        "Роль",
        max_length=20,
        choices=Role.choices,
        default=Role.GUEST,
    )

    def __str__(self) -> str:
        return self.username


class Following(models.Model):
    user_id = models.ForeignKey(FoodgramUser, related_name="following")
    following_user_id = models.ForeignKey(FoodgramUser, related_name="followers")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["used_id", "following_user_id"],
                name="unique_followers",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user_id} follows {self.following_user_id}."
