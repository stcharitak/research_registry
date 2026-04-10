from accounts.models import RoleName
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrResearcher(BasePermission):
    def has_permission(self, request, _view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if not user.role:
            return False

        return user.role.name in [RoleName.ADMIN, RoleName.RESEARCHER]


class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, _view):
        if request.method in SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_authenticated)


class CanAccessApplication(IsAdminOrResearcher):
    admin_only_actions = {"approve", "reject", "destroy"}
    allowed_actions = {
        "list",
        "retrieve",
        "create",
        "update",
        "partial_update",
        "approve",
        "reject",
        "destroy",
    }

    def has_permission(self, request, view):
        user = request.user

        if not super().has_permission(request, view):
            return False

        action = getattr(view, "action", None)

        if action in self.admin_only_actions:
            return user.role.name == RoleName.ADMIN

        if action in self.allowed_actions:
            return user.role.name in [RoleName.ADMIN, RoleName.RESEARCHER]

        return False

    def has_object_permission(self, request, _view, obj):
        user = request.user

        if not user.role:
            return False

        if user.role.name == RoleName.ADMIN:
            return True

        if user.role.name == RoleName.RESEARCHER:
            return obj.study.created_by == user or obj.reviewed_by == user

        return False
