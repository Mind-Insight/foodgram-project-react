from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, object):
        return (
            request.method in permissions.SAFE_METHODS
            or object.author == request.user
            and request.user.is_authenticated
        )


from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """Автор объекта имеет разрешение на доступ."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and obj.author == request.user
        )