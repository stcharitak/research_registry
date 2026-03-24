from rest_framework.viewsets import ModelViewSet

from .models import Study
from .serializers import (
    StudyDetailSerializer,
    StudyListSerializer,
    StudyWriteSerializer,
)
from core.permissions import IsAuthenticatedOrReadOnly


class StudyViewSet(ModelViewSet):
    queryset = Study.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    filterset_fields = ["status", "created_by"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]

    def get_serializer_class(self):
        if self.action == "list":
            return StudyListSerializer

        if self.action in ["create", "update", "partial_update"]:
            return StudyWriteSerializer

        return StudyDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
