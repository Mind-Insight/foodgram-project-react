from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets
from django.contrib.auth import get_user_model

from users.models import Following
from .serializers import UserRegistrationSerializer

User = get_user_model()


class UserRegistrationViewSet(viewsets.ModelViewset):
    serializer_class = UserRegistrationSerializer


class UserFollowingViewSet(viewsets.ModelViewset):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserFollowingSerializer
    queryset = Following.objects.all()