from rest_framework import serializers

from .models import Application
from participants.serializers import ParticipantSerializer
from studies.serializers import StudyListSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    participant_detail = ParticipantSerializer(
        source="participant",
        read_only=True,
    )
    study_detail = StudyListSerializer(
        source="study",
        read_only=True,
    )
    reviewed_by_username = serializers.CharField(
        source="reviewed_by.username",
        read_only=True,
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "participant",
            "participant_detail",
            "study",
            "study_detail",
            "status",
            "notes",
            "reviewed_by",
            "reviewed_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "participant_detail",
            "study_detail",
            "reviewed_by_username",
            "created_at",
            "updated_at",
        ]
