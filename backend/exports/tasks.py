from applications.services import ApplicationExportService
from celery import shared_task
from django.utils import timezone

from .models import ExportJob, ExportJobStatus, ExportType


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def run_export_job(_task, export_job_id: int):
    job = ExportJob.objects.get(id=export_job_id)

    job.status = ExportJobStatus.PROCESSING
    job.started_at = timezone.now()
    job.error_message = ""
    job.save(update_fields=["status", "started_at", "error_message"])

    try:
        if job.export_type == ExportType.APPLICATIONS:
            ApplicationExportService.generate_csv_file(job)
        else:
            raise ValueError(f"Unsupported export type: {job.export_type}")

        job.status = ExportJobStatus.COMPLETED
        job.finished_at = timezone.now()
        job.save(update_fields=["file", "status", "finished_at"])
    except Exception as exc:
        job.status = ExportJobStatus.FAILED
        job.finished_at = timezone.now()
        job.error_message = str(exc)
        job.save(update_fields=["status", "finished_at", "error_message"])
        raise
