from core.permissions import CanAccessApplication
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from applications.services import ApplicationService

from .filters import ApplicationFilter
from .serializers import ApplicationReadSerializer, ApplicationWriteSerializer


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
        return ApplicationService.get_visible_applications(self.request.user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ApplicationReadSerializer

        return ApplicationWriteSerializer

    def perform_create(self, serializer):
        serializer.instance = ApplicationService.create_application(
            user=self.request.user,
            validated_data=serializer.validated_data,
        )

    def perform_update(self, serializer):
        serializer.instance = ApplicationService.update_application(
            application=self.get_object(),
            user=self.request.user,
            validated_data=serializer.validated_data,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        _ = pk
        application = self.get_object()

        application = ApplicationService.approve(application, request.user)
        serializer = self.get_serializer(application)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        _ = pk
        application = self.get_object()

        application = ApplicationService.reject(application, request.user)
        serializer = self.get_serializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)
