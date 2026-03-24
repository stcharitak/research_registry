from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrResearcher(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if not user.role:
            return False

        return user.role.name in ["admin", "researcher"]


class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_authenticated)
