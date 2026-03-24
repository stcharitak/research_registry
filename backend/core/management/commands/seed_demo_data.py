import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Role
from applications.models import Application
from participants.models import Participant
from studies.models import Study


BASE_DIR = Path(settings.BASE_DIR)
SEED_DIR = BASE_DIR / "core" / "seed_data"


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


class Command(BaseCommand):
    help = "Seed demo data from JSON"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        for data in load_json("users.json"):
            role = Role.objects.get(name=data["role"])

            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "role": role,
                    "is_staff": data["is_staff"],
                    "is_superuser": data["is_superuser"],
                },
            )

            if created:
                user.set_password(data["password"])
                user.save()

        for data in load_json("studies.json"):
            created_by = User.objects.get(username=data["created_by"])

            Study.objects.get_or_create(
                title=data["title"],
                defaults={
                    "description": data["description"],
                    "status": data["status"],
                    "created_by": created_by,
                },
            )

        for data in load_json("participants.json"):
            Participant.objects.get_or_create(
                code=data["code"],
                defaults=data,
            )

        for data in load_json("applications.json"):
            participant = Participant.objects.get(code=data["participant"])
            study = Study.objects.get(title=data["study"])

            reviewed_by = None
            if data["reviewed_by"]:
                reviewed_by = User.objects.get(username=data["reviewed_by"])

            Application.objects.get_or_create(
                participant=participant,
                study=study,
                defaults={
                    "status": data["status"],
                    "notes": data["notes"],
                    "reviewed_by": reviewed_by,
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded"))
