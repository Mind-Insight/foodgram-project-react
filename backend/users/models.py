from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

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
    first_name = models.CharField(
        "Имя",
        max_length=100,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=100,
    )
    role = models.CharField(
        "Роль",
        max_length=20,
        choices=Role.choices,
        default=Role.GUEST,
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def clean(self):
        if len(set([self.username, self.first_name, self.last_name])) != 3:
            raise ValidationError(
                "Поля username, name, surname должны быть уникальными в пределах одной записи"
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            models.Index(
                fields=["first_name", "last_name"],
                name="user_index_fields",
            )
        ]

    def __str__(self) -> str:
        return self.username


class Following(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following_user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="followers",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following_user"],
                name="unique_followers_constratints",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} follows {self.following_user}."
