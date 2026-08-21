import csv
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Import test users from CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="csv_data/products/users.csv",
            help="Path to the users CSV file.",
        )

    def handle(self, *args, **options):
        csv_file = Path(options["path"])

        if not csv_file.exists():
            raise CommandError(f"CSV file not found:\n{csv_file}")

        User = get_user_model()

        with open(
            csv_file,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                username = row["username"]

                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": row["email"],
                        "first_name": row["first_name"],
                        "last_name": row["last_name"],
                    },
                )

                if created:
                    user.set_password(row["password"])
                    user.save()

                    self.stdout.write(self.style.SUCCESS(f"✓ Created user: {username}"))
                else:
                    self.stdout.write(f"↻ User already exists: {username}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Test users imported successfully."))
