from accounts.models import RoleName
from django.conf import settings
from django.db import models
from django.db.models import Q
from participants.models import Participant
from studies.models import Study


class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class ApplicationQuerySet(models.QuerySet):
    def for_user(self, user):
        if not user or not user.is_authenticated:
            return self.none()

        role_name = getattr(getattr(user, "role", None), "name", None)

        if role_name == RoleName.ADMIN:
            return self

        if role_name == RoleName.RESEARCHER:
            return self.filter(
                Q(study__created_by=user) | Q(reviewed_by=user)
            ).distinct()

        return self.none()

    def pending(self):
        return self.filter(status=Status.PENDING)

    def approved(self):
        return self.filter(status=Status.APPROVED)

    def rejected(self):
        return self.filter(status=Status.REJECTED)


class ApplicationManager(models.Manager.from_queryset(ApplicationQuerySet)):
    pass


class Application(models.Model):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    notes = models.TextField(
        blank=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "study"],
                name="unique_participant_study_application",
            )
        ]

    objects = ApplicationManager()

    def __str__(self) -> str:
        return f"Application #{self.pk}"


class ApplicationLogAction(models.TextChoices):
    CREATED = "created", "Created"
    UPDATED = "updated", "Updated"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class ApplicationLog(models.Model):
    application = models.ForeignKey(
        "Application",
        on_delete=models.CASCADE,
        related_name="logs",
    )

    action = models.CharField(
        max_length=20,
        choices=ApplicationLogAction.choices,
    )

    performed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_logs",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.application_id} - {self.action}"
