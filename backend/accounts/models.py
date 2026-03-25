from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager


class RoleName(models.TextChoices):
    ADMIN = "admin", "Admin"
    RESEARCHER = "researcher", "Researcher"


class Role(models.Model):
    """User role in the system (admin, researcher, etc.)."""

    name = models.CharField(max_length=50, unique=True, choices=RoleName.choices)
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)


class UserManager(DjangoUserManager):
    """Overrides Superuser method and on create add admin role."""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        user = super().create_superuser(username, password, **extra_fields)

        admin_role, _ = Role.objects.get_or_create(
            name=RoleName.ADMIN,
            defaults={"description": "Administrator"},
        )

        user.role = admin_role
        user.save()

        return user


class User(AbstractUser):
    """Custom user with role relation."""

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )

    objects = UserManager()

    def __str__(self):
        if self.role:
            return f"{self.username} ({self.role.name})"
        return self.username
