from rest_framework.viewsets import ModelViewSet

from .models import Application, Status
from accounts.models import RoleName
from .serializers import ApplicationReadSerializer, ApplicationWriteSerializer
from core.permissions import CanAccessApplication
from rest_framework.decorators import action
from rest_framework.response import Response


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    permission_classes = [CanAccessApplication]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated or not user.role:
            return Application.objects.none()

        if user.role.name == RoleName.ADMIN:
            return Application.objects.all()

        if user.role.name == RoleName.RESEARCHER:
            return Application.objects.filter(study__created_by=user)

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

        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        application = self.get_object()

        application.status = Status.REJECTED
        application.reviewed_by = request.user
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)
