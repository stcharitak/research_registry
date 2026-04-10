import csv
import os
import tempfile
from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.db import transaction
from django.utils import timezone
from exports.models import ExportJob

from .models import Application, ApplicationLog, ApplicationLogAction, RoleName, Status


class ApplicationService:
    @staticmethod
    def get_visible_applications(user):
        return Application.objects.for_user(user).select_related(
            "study", "participant", "reviewed_by", "study__created_by"
        )

    @staticmethod
    @transaction.atomic
    def update_application(*, application, user, validated_data):
        study = validated_data.get("study", application.study)

        role_name = getattr(getattr(user, "role", None), "name", None)

        if role_name == RoleName.RESEARCHER and study.created_by != user:
            raise PermissionDenied("You cannot assign this application to this study.")

        changed_fields = []

        for field, value in validated_data.items():
            current_value = getattr(application, field)
            if current_value != value:
                setattr(application, field, value)
                changed_fields.append(field)

        if changed_fields:
            application.save(update_fields=changed_fields)

            ApplicationLog.objects.create(
                application=application,
                action=ApplicationLogAction.UPDATED,
                performed_by=user,
                note=f"Application updated: {', '.join(changed_fields)}",
            )

        return application

    @staticmethod
    @transaction.atomic
    def create_application(*, user, validated_data):
        study = validated_data["study"]

        role_name = getattr(getattr(user, "role", None), "name", None)

        if role_name == RoleName.RESEARCHER and study.created_by != user:
            raise PermissionDenied("You cannot create an application for this study.")

        application = Application.objects.create(**validated_data)

        ApplicationLog.objects.create(
            application=application,
            action=ApplicationLogAction.CREATED,
            performed_by=user,
            note="Application created",
        )

        return application

    @staticmethod
    @transaction.atomic
    def approve(application, reviewer):
        role_name = getattr(getattr(reviewer, "role", None), "name", None)
        if role_name != RoleName.ADMIN:
            raise PermissionDenied("Only admins can approve applications.")

        application.status = Status.APPROVED

        application.reviewed_by = reviewer
        application.created_at = timezone.now()
        application.save(update_fields=["status", "reviewed_by", "created_at"])

        ApplicationLog.objects.create(
            application=application,
            performed_by=reviewer,
            action=ApplicationLogAction.APPROVED,
            note="Application approved",
        )

        return application

    @staticmethod
    @transaction.atomic
    def reject(application, reviewer):
        role_name = getattr(getattr(reviewer, "role", None), "name", None)
        if role_name != RoleName.ADMIN:
            raise PermissionDenied("Only admins can reject applications.")

        application.status = Status.REJECTED

        application.reviewed_by = reviewer
        application.created_at = timezone.now()
        application.save(update_fields=["status", "reviewed_by", "created_at"])

        ApplicationLog.objects.create(
            application=application,
            performed_by=reviewer,
            action=ApplicationLogAction.REJECTED,
            note="Application rejected",
        )

        return application


class ApplicationExportService:
    HEADER = [
        "id",
        "study_title",
        "participant_name",
        "participant_email",
        "status",
        "reviewed_by",
        "created_at",
        "updated_at",
    ]

    @staticmethod
    def _base_queryset_for_user(user):
        queryset = Application.objects.select_related(
            "study",
            "participant",
            "reviewed_by",
        ).order_by("id")

        role_name = getattr(user.role, "name", None)

        if role_name == RoleName.ADMIN:
            return queryset

        if role_name == RoleName.RESEARCHER:
            return queryset.filter(study__created_by=user)

        return queryset.none()

    @classmethod
    def build_queryset(cls, job: ExportJob):
        queryset = cls._base_queryset_for_user(job.requested_by)
        status_value = job.filters.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)

        study_id = job.filters.get("study_id")
        if study_id:
            queryset = queryset.filter(study_id=study_id)

        participant_id = job.filters.get("participant_id")
        if participant_id:
            queryset = queryset.filter(participant_id=participant_id)

        reviewed_by_id = job.filters.get("reviewed_by_id")
        if reviewed_by_id is None:
            # Backward-compatible alias: accept reviewed_by as reviewer user id.
            reviewed_by_id = job.filters.get("reviewed_by")
        if reviewed_by_id:
            queryset = queryset.filter(reviewed_by_id=reviewed_by_id)

        return queryset

    @classmethod
    def generate_csv_file(cls, job: ExportJob):
        queryset = cls.build_queryset(job)

        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            suffix=".csv",
            delete=False,
            encoding="utf-8",
        ) as tmp:
            writer = csv.writer(tmp)
            writer.writerow(cls.HEADER)

            for application in queryset.iterator(chunk_size=2000):
                participant_name = getattr(application.participant, "full_name", None)
                if not participant_name:
                    first_name = getattr(application.participant, "first_name", "")
                    last_name = getattr(application.participant, "last_name", "")
                    participant_name = f"{first_name} {last_name}".strip()

                writer.writerow(
                    [
                        application.id,
                        application.study.title,
                        participant_name,
                        application.participant.email,
                        application.status,
                        application.reviewed_by.email
                        if application.reviewed_by
                        else "",
                        application.created_at.isoformat()
                        if application.created_at
                        else "",
                        application.updated_at.isoformat()
                        if application.updated_at
                        else "",
                    ]
                )

            tmp_path = tmp.name

        filename = f"applications_export_{job.id}_{datetime.now().date()}.csv"

        with open(tmp_path, "rb") as f:
            job.file.save(filename, File(f), save=False)

        os.remove(tmp_path)

        return job
