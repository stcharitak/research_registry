from django.contrib import admin
from .models import Application, ApplicationLog


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "participant",
        "study",
        "status",
        "reviewed_by",
        "created_at",
    )

    list_filter = (
        "status",
        "study",
    )

    search_fields = (
        "participant__code",
        "participant__last_name",
        "study__title",
    )


@admin.register(ApplicationLog)
class ApplicationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "action", "performed_by", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("application__id", "performed_by__username", "note")
