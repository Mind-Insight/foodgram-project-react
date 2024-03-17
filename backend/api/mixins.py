from rest_framework import serializers

from recipes.models import Recipe


class RecipeSerializerMixin(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    image_url = serializers.SerializerMethodField(
        "get_image_url",
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            "author",
            "title",
            "image",
            "description",
            "ingredients",
            "tags",
            "time",
        )
        read_only_fields = ("author",)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
