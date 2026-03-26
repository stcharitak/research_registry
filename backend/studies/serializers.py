from rest_framework import serializers

from .models import Study


class StudyListSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = Study
        fields = [
            "id",
            "title",
            "description",
            "status",
            "created_by",
            "created_by_username",
        ]


class StudyDetailSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = Study
        fields = [
            "id",
            "title",
            "description",
            "status",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]


class StudyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = [
            "title",
            "description",
            "status",
        ]
