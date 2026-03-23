from django.contrib import admin
from .models import Study


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "created_by",
        "created_at",
    )

    list_filter = ("status",)

    search_fields = ("title",)
