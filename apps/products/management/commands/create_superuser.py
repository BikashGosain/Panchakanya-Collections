import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the initial superuser from environment variables."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Superuser environment variables are not set. "
                    "Skipping superuser creation."
                )
            )
            return

        user = User.objects.filter(username=username).first()

        if user:
            if not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=["is_staff", "is_superuser"])

            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' already exists.")
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email or "",
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(f"Superuser '{user.username}' created successfully.")
        )
