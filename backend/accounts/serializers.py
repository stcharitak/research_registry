from rest_framework import serializers

from .models import User


class MeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "is_staff",
            "is_superuser",
        ]
