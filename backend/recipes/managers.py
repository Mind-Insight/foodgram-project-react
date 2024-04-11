from django.db.models import QuerySet, Manager, Exists, OuterRef, Prefetch

from users.models import Following
from django.contrib.auth import get_user_model

User = get_user_model()


class RecipeManager(Manager):
    def annotate_user_flags(self, user):
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
            .prefetch_related(
                Prefetch(
                    "author",
                    queryset=User.objects.annotate(
                        is_subscribed=Exists(
                            queryset=(
                                Following.objects.filter(
                                    user=user, author=OuterRef("pk")
                                )
                            )
                        )
                    ),
                )
            )
        )
