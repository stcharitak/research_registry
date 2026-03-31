from getpass import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Role, RoleName


class Command(BaseCommand):
    help = "Interactively create a researcher user"

    def handle(self, *args, **options):
        User = get_user_model()

        username = input("Username: ").strip()
        if not username:
            raise CommandError("Username is required.")

        if User.objects.filter(username=username).exists():
            raise CommandError(f"User '{username}' already exists.")

        email = input("Email (optional): ").strip()

        password = getpass("Password: ")
        if not password:
            raise CommandError("Password is required.")

        password_confirm = getpass("Confirm password: ")
        if password != password_confirm:
            raise CommandError("Passwords do not match.")

        researcher_role, _ = Role.objects.get_or_create(
            name=RoleName.RESEARCHER,
            defaults={"description": "Research user"},
        )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=researcher_role,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Researcher user '{user.username}' created successfully."
            )
        )
