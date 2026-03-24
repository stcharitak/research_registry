from rest_framework.viewsets import ModelViewSet

from .models import Participant
from .serializers import ParticipantSerializer
from core.permissions import IsAdminOrResearcher


class ParticipantViewSet(ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = [IsAdminOrResearcher]
