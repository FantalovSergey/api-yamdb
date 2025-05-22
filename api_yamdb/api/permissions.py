from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение на изменение только для автора.
    Остальные могут только просматривать.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author_id == request.user.id
            or request.user.is_staff
        )
    