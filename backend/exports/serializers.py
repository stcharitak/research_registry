from rest_framework import serializers

from .models import ExportJob, ExportType


class ExportJobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportJob
        fields = ["id", "export_type", "filters"]
        read_only_fields = ["id"]

    def validate_export_type(self, value):
        if value not in ExportType:
            raise serializers.ValidationError(f"Unsupported export type '{value}'.")
        return value


class ExportJobReadSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ExportJob
        fields = [
            "id",
            "export_type",
            "status",
            "filters",
            "error_message",
            "created_at",
            "started_at",
            "finished_at",
            "download_url",
        ]

    def get_download_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
