from rest_framework.viewsets import ModelViewSet

from .models import Study
from .serializers import (
    StudyDetailSerializer,
    StudyListSerializer,
    StudyWriteSerializer,
)


class StudyViewSet(ModelViewSet):
    queryset = Study.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return StudyListSerializer

        if self.action in ["create", "update", "partial_update"]:
            return StudyWriteSerializer

        return StudyDetailSerializer
