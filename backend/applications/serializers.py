from rest_framework import serializers
from studies.serializers import StudyListSerializer

from .models import Application, ApplicationLog, ApplicationLogAction


class ApplicationReadSerializer(serializers.ModelSerializer):
    study = StudyListSerializer()
    participant = serializers.StringRelatedField()
    reviewed_by = serializers.StringRelatedField()

    class Meta:
        model = Application
        fields = "__all__"


class ApplicationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "study",
            "participant",
            "notes",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        application = Application.objects.create(
            **validated_data,
            reviewed_by=request.user,
            status="pending",
        )

        ApplicationLog.objects.create(
            application=application,
            action=ApplicationLogAction.CREATED,
            performed_by=request.user,
        )

        return application

    def update(self, instance, validated_data):
        # prevent status change from client
        validated_data.pop("status", None)
        validated_data.pop("reviewed_by", None)
        application = super().update(instance, validated_data)
        request = self.context["request"]

        ApplicationLog.objects.create(
            application=application,
            action=ApplicationLogAction.UPDATED,
            performed_by=request.user,
        )

        return application
