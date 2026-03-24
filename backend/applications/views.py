from rest_framework.viewsets import ModelViewSet

from .models import Application
from .serializers import ApplicationSerializer
from core.permissions import IsAdminOrResearcher


class ApplicationViewSet(ModelViewSet):
    queryset = Application.objects.all()
    permission_classes = [IsAdminOrResearcher]
    serializer_class = ApplicationSerializer
