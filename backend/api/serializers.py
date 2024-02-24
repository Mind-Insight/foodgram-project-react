from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

from users.models import Following

User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "username",
            "name",
            "surname",
            "email",
            "password",
        )


class FollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Following
        fields = (
            "id",
            "following_user_id",
            "created",
        )


class FollowersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Following
        fields = (
            "id",
            "user_id",
            "created",
        )


class UserSerializer(serializers.ModelSerializer):

    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "following",
            "followers",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_following(self, obj):
        return FollowingSerializer(obj.following.all(), many=True).data

    def get_followers(self, obj):
        return FollowersSerializer(obj.followers.all(), many=True).data
