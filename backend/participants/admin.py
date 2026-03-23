from django.contrib import admin
from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "first_name",
        "last_name",
        "email",
        "consent",
        "created_at",
    )

    search_fields = (
        "code",
        "last_name",
        "email",
    )
