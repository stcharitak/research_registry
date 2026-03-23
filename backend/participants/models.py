from django.db import models


class Participant(models.Model):
    """Participant."""

    code = models.CharField(
        max_length=20,
        unique=True,
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    email = models.EmailField()

    birth_year = models.IntegerField(
        null=True,
        blank=True,
    )

    consent = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self) -> str:
        return f"{self.code} - {self.last_name}"
