from django.db import transaction
from django.utils import timezone

from .models import Application, ApplicationLog, ApplicationLogAction, Status, RoleName
from django.core.exceptions import PermissionDenied


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
