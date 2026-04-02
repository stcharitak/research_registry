from accounts.models import User
from participants.models import Participant
from rest_framework import serializers
from studies.models import Study

from .models import Application, ApplicationLog


class SimpleUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class SimpleStudySerializer(serializers.ModelSerializer):
    created_by = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Study
        fields = ["id", "title", "created_by"]


class SimpleParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ["id", "first_name", "last_name"]


class ApplicationLogSerializer(serializers.ModelSerializer):
    performed_by = SimpleUserSerializer(read_only=True)

    class Meta:
        model = ApplicationLog
        fields = [
            "id",
            "action",
            "note",
            "performed_by",
            "created_at",
        ]


class ApplicationReadSerializer(serializers.ModelSerializer):
    study = SimpleStudySerializer(read_only=True)
    participant = SimpleParticipantSerializer(read_only=True)
    reviewed_by = SimpleUserSerializer(read_only=True)
    logs = ApplicationLogSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "study",
            "participant",
            "status",
            "reviewed_by",
            "notes",
            "logs",
            "created_at",
            "updated_at",
        ]


class ApplicationWriteSerializer(serializers.ModelSerializer):
    study = serializers.PrimaryKeyRelatedField(queryset=Study.objects.all())
    participant = serializers.PrimaryKeyRelatedField(queryset=Participant.objects.all())

    class Meta:
        model = Application
        fields = [
            "id",
            "study",
            "participant",
            "notes",
        ]
        read_only_fields = ["id"]
