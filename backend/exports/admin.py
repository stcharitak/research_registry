from django.contrib import admin

from .models import ExportJob


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "requested_by",
        "export_type",
        "status",
        "created_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("export_type", "status", "created_at")
    search_fields = ("requested_by__email",)
