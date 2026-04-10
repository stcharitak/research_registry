from accounts.models import Role, RoleName
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default roles"

    def handle(self, *_args, **_kwargs):
        roles = [
            (RoleName.ADMIN, "Full access"),
            (RoleName.RESEARCHER, "Research user"),
        ]

        for name, description in roles:
            Role.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )

        self.stdout.write(self.style.SUCCESS("Roles created"))
