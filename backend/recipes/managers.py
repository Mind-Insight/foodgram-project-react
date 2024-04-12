from django.db.models import Manager, Exists, OuterRef
from django.contrib.auth import get_user_model

from users.models import Following

User = get_user_model()


class RecipeManager(Manager):
    def get_correct_user(self, user):
        return (
            self.annotate(
                is_in_shopping_cart=Exists(
                    queryset=User.objects.filter(
                        id=user.id, shopping_list=OuterRef("pk")
                    )
                )
            )
            .annotate(
                is_favorited=Exists(
                    queryset=User.objects.filter(id=user.id, favorites=OuterRef("pk"))
                )
            )
            .annotate(
                is_subscribed=Exists(
                    queryset=Following.objects.filter(user=user, author=OuterRef("pk"))
                )
            )
        )
