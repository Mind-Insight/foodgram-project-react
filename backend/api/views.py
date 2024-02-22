from rest_framework import viewsets
from django.contrib.auth import get_user_model

from .serializers import UserRegistrationSerializer

User = get_user_model()


class UserRegistrationViewSet(viewsets.ModelViewset):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer