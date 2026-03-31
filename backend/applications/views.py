from rest_framework.viewsets import ModelViewSet

from .models import Application, Status, ApplicationLog, ApplicationLogAction
from accounts.models import RoleName
from .serializers import ApplicationReadSerializer, ApplicationWriteSerializer
from core.permissions import CanAccessApplication
from rest_framework.decorators import action
from rest_framework.response import Response
from .filters import ApplicationFilter
from django.db.models import Q


class ApplicationViewSet(ModelViewSet):
    permission_classes = [CanAccessApplication]
    filterset_class = ApplicationFilter

    search_fields = [
        "status",
        "study__id",
        "participant__id",
        "reviewed_by__username",
    ]

    ordering_fields = [
        "id",
        "status",
        "reviewed_by",
    ]

    ordering = ["-id"]

    def get_queryset(self):
        user = self.request.user

        base_queryset = Application.objects.select_related(
            "study",
            "participant",
            "reviewed_by",
            "study__created_by",
        ).prefetch_related(
            "logs",
            "logs__performed_by",
        )

        if not user.is_authenticated or not user.role:
            return Application.objects.none()

        if user.role.name == RoleName.ADMIN:
            return base_queryset

        if user.role.name == RoleName.RESEARCHER:
            return base_queryset.filter(
                Q(study__created_by=user) | Q(reviewed_by=user)
            ).distinct()

        return Application.objects.none()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ApplicationReadSerializer

        return ApplicationWriteSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        application = self.get_object()

        application.status = Status.APPROVED
        application.reviewed_by = request.user
        application.save()

        ApplicationLog.objects.create(
            application=application,
            action=ApplicationLogAction.APPROVED,
            performed_by=request.user,
        )

        serializer = self.get_serializer(application)

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        application = self.get_object()

        application.status = Status.REJECTED
        application.reviewed_by = request.user
        application.save()

        ApplicationLog.objects.create(
            application=application,
            action=ApplicationLogAction.REJECTED,
            performed_by=request.user,
        )

        serializer = self.get_serializer(application)

        return Response(serializer.data)
