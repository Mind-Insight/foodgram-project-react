from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):

    email = models.EmailField(
        "Электронная почта",
        max_length=254,
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
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    # def clean(self):
    #     if len(set([self.username, self.first_name, self.last_name])) != 3:
    #         raise ValidationError(
    #             "Поля username, name, surname должны "
    #             "быть уникальными в пределах одной записи"
    #         )
    #     super().clean()

    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            models.Index(
                fields=["first_name", "last_name"],
                name="user_index_fields",
            )
        ]


class Following(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_followers_constratints",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} follows {self.author}."
