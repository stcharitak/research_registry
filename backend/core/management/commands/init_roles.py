from django.core.management.base import BaseCommand
from accounts.models import Role


class Command(BaseCommand):
    help = "Create default roles"

    def handle(self, *args, **kwargs):
        roles = [
            ("admin", "Full access"),
            ("researcher", "Research user"),
        ]

        for name, description in roles:
            Role.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )

        self.stdout.write(self.style.SUCCESS("Roles created"))
