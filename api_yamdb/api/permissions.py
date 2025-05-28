from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Доступ только с правами администратора."""
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """Доступ только с правами администратора,
    а также при безопасных запросах."""
    def has_permission(self, request, view):
        user = request.user
        return (request.method in SAFE_METHODS
                or user.is_authenticated and user.is_admin)


class IsAuthorOrModeratorOrReadOnly(BasePermission):
    """Разрешение на редактирование только с правами модератора,
    а также авторам редактируемых объектов."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or obj.author == user
            or user.is_authenticated and (user.is_moderator or user.is_admin)
        )
