from rest_framework import serializers

from recipes.models import Recipe


class RecipeSerializerMixin(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(
        "get_image_url",
        read_only=True,
    )
    is_favorited = serializers.BooleanField(
        default=False,
    )
    is_in_shopping_cart = serializers.BooleanField(
        default=False,
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("author",)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
