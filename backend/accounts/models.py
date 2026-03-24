from django.contrib.auth.models import AbstractUser
from django.db import models


class RoleName(models.TextChoices):
    ADMIN = "admin", "Admin"
    RESEARCHER = "researcher", "Researcher"


class Role(models.Model):
    """User role in the system (admin, researcher, etc.)."""

    name = models.CharField(max_length=50, unique=True, choices=RoleName.choices)
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)


class User(AbstractUser):
    """Custom user with role relation."""

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.role:
            return f"{self.username} ({self.role.name})"
        return self.username
