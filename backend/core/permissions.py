from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.models import RoleName


class IsAdminOrResearcher(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if not user.role:
            return False

        return user.role.name in [RoleName.ADMIN, RoleName.RESEARCHER]


class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_authenticated)


class CanAccessApplication(IsAdminOrResearcher):
    def has_permission(self, request, view):
        user = request.user

        if not super().has_permission(request, view):
            return False

        if view.action in ["approve", "reject", "destroy"]:
            return user.role.name == RoleName.ADMIN

        if view.action in ["list", "retrieve", "create", "update", "partial_update"]:
            return user.role.name in [RoleName.ADMIN, RoleName.RESEARCHER]

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.role:
            return False

        if user.role.name == RoleName.ADMIN:
            return True

        if user.role.name == RoleName.RESEARCHER:
            return obj.study.created_by == user

        return False
