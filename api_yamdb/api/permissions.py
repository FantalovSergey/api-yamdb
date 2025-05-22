from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return (not user.is_anonymous and (user.role == 'admin'
                                           or user.is_superuser))


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or user.role == 'admin'
            or user.is_superuser
        )


class IsAuthorOrModeratorOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or user.role in ('admin', 'moderator')
            or user.is_superuser
        )
