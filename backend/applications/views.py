from rest_framework.viewsets import ModelViewSet

from .models import Application
from .serializers import ApplicationSerializer
from core.permissions import CanAccessApplication
from rest_framework.decorators import action
from rest_framework.response import Response


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [CanAccessApplication]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        application = self.get_object()

        application.status = "approved"
        application.reviewed_by = request.user
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        application = self.get_object()

        application.status = "rejected"
        application.reviewed_by = request.user
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)

    serializer_class = ApplicationSerializer
