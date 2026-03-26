from rest_framework import serializers

from .models import Application


class ApplicationReadSerializer(serializers.ModelSerializer):
    study = serializers.StringRelatedField()
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
            created_by=request.user,
            status="pending",
        )

        return application

    def update(self, instance, validated_data):
        # prevent status change from client
        validated_data.pop("status", None)
        validated_data.pop("reviewed_by", None)
        validated_data.pop("created_by", None)

        return super().update(instance, validated_data)
