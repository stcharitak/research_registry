from django.conf import settings
from django.db import models


class ExportType(models.TextChoices):
    APPLICATIONS = "applications", "Applications"
    STUDIES = "studies", "Studies"
    PARTICIPANTS = "participants", "Participants"


class ExportJobStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class ExportJob(models.Model):
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="export_jobs",
    )
    export_type = models.CharField(
        max_length=50,
        choices=ExportType.choices,
        default=ExportType.APPLICATIONS,
    )
    status = models.CharField(
        max_length=20,
        choices=ExportJobStatus.choices,
        default=ExportJobStatus.PENDING,
    )
    filters = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to="exports/", null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ExportJob {self.id} - {self.export_type} - {self.status}"
