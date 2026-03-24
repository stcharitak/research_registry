from rest_framework.viewsets import ModelViewSet

from .models import Study
from .serializers import StudySerializer


class StudyViewSet(ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudySerializer
