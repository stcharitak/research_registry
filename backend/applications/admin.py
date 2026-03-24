from django.contrib import admin
from .models import Application


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
