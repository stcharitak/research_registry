from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        RESEARCHER = "researcher", "Researcher"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.RESEARCHER,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"