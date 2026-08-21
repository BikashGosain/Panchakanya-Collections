import csv
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.products.models import Product
from apps.reviews.models import Review


class Command(BaseCommand):
    help = "Import test reviews from CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="csv_data/products",
            help="Directory containing products.csv and reviews.csv.",
        )

    # =============================================================
    # CSV HELPERS
    # =============================================================

    def clean_row(self, row):
        cleaned = {}

        for key, value in row.items():
            if key is None:
                continue

            clean_key = key.strip().lstrip("\ufeff")

            if value is None:
                clean_value = ""
            else:
                clean_value = value.strip()

            cleaned[clean_key] = clean_value

        return cleaned

    def read_csv(self, file_path, required_columns):
        if not file_path.exists():
            raise CommandError(f"CSV file not found:\n{file_path}")

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:
                reader = csv.DictReader(file)

                if reader.fieldnames is None:
                    raise CommandError(f"CSV file has no header:\n{file_path}")

                headers = [
                    header.strip().lstrip("\ufeff") for header in reader.fieldnames
                ]

                missing_columns = [
                    column for column in required_columns if column not in headers
                ]

                if missing_columns:
                    raise CommandError(
                        f"\nInvalid CSV header in:\n"
                        f"{file_path}\n\n"
                        f"Expected columns:\n"
                        f"{required_columns}\n\n"
                        f"Found columns:\n"
                        f"{headers}\n\n"
                        f"Missing columns:\n"
                        f"{missing_columns}"
                    )

                rows = []

                for line_number, row in enumerate(reader, start=2):
                    cleaned_row = self.clean_row(row)

                    if not any(cleaned_row.values()):
                        continue

                    cleaned_row["_line_number"] = line_number
                    rows.append(cleaned_row)

                return rows

        except UnicodeDecodeError as exc:
            raise CommandError(
                f"Could not read CSV file:\n"
                f"{file_path}\n\n"
                f"Make sure the file is saved as UTF-8.\n\n"
                f"Error: {exc}"
            )

    # =============================================================
    # MAIN
    # =============================================================

    @transaction.atomic
    def handle(self, *args, **options):

        csv_dir = Path(options["path"])

        products_file = csv_dir / "products.csv"
        reviews_file = csv_dir / "reviews.csv"

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("========================================")
        )
        self.stdout.write(self.style.SUCCESS("       TEST REVIEW IMPORT"))
        self.stdout.write(
            self.style.SUCCESS("========================================")
        )
        self.stdout.write("")

        # =========================================================
        # 1. READ PRODUCTS CSV
        # =========================================================

        self.stdout.write(self.style.WARNING("Reading products.csv..."))

        product_rows = self.read_csv(
            products_file,
            [
                "id",
                "sku",
            ],
        )

        # =========================================================
        # 2. BUILD CSV PRODUCT ID -> ACTUAL DJANGO PRODUCT
        # =========================================================

        product_map = {}

        for row in product_rows:
            line_number = row["_line_number"]

            try:
                csv_product_id = int(row["id"])
            except ValueError:
                raise CommandError(
                    f"Invalid product ID on CSV line {line_number}: {row['id']}"
                )

            sku = row["sku"]

            product = Product.objects.filter(sku=sku).first()

            if product is None:
                raise CommandError(
                    f"Product with SKU '{sku}' from products.csv "
                    f"does not exist in the database."
                )

            product_map[csv_product_id] = product

        self.stdout.write(self.style.SUCCESS(f"✓ Products mapped: {len(product_map)}"))

        # =========================================================
        # 3. READ REVIEWS CSV
        # =========================================================

        self.stdout.write(self.style.WARNING("Reading reviews.csv..."))

        review_rows = self.read_csv(
            reviews_file,
            [
                "username",
                "product_id",
                "rating",
                "comment",
                "is_deleted",
            ],
        )

        User = get_user_model()

        # =========================================================
        # 4. IMPORT REVIEWS
        # =========================================================

        created_count = 0
        updated_count = 0

        for row in review_rows:
            line_number = row["_line_number"]

            # -----------------------------------------------------
            # Username
            # -----------------------------------------------------

            username = row["username"]

            if not username:
                raise CommandError(f"Username is empty on CSV line {line_number}.")

            user = User.objects.filter(username=username).first()

            if user is None:
                raise CommandError(
                    f"User '{username}' does not exist on CSV line {line_number}."
                )

            # -----------------------------------------------------
            # CSV Product ID
            # -----------------------------------------------------

            try:
                csv_product_id = int(row["product_id"])
            except ValueError:
                raise CommandError(
                    f"Invalid product_id on CSV line {line_number}: {row['product_id']}"
                )

            product = product_map.get(csv_product_id)

            if product is None:
                raise CommandError(
                    f"Product with CSV ID {csv_product_id} "
                    f"does not exist in products.csv "
                    f"on CSV line {line_number}."
                )

            # -----------------------------------------------------
            # Rating
            # -----------------------------------------------------

            try:
                rating = int(row["rating"])
            except ValueError:
                raise CommandError(
                    f"Invalid rating on CSV line {line_number}: {row['rating']}"
                )

            if rating < 1 or rating > 5:
                raise CommandError(
                    f"Rating must be between 1 and 5 on CSV line {line_number}."
                )

            # -----------------------------------------------------
            # Comment
            # -----------------------------------------------------

            comment = row["comment"]

            # -----------------------------------------------------
            # is_deleted
            # -----------------------------------------------------

            is_deleted = row["is_deleted"].lower() in {
                "true",
                "1",
                "yes",
            }

            # -----------------------------------------------------
            # Create / update review
            # -----------------------------------------------------

            _review, created = Review.objects.update_or_create(
                user=user,
                product=product,
                defaults={
                    "rating": rating,
                    "comment": comment,
                    "is_deleted": is_deleted,
                },
            )

            if created:
                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Created review: {username} → {product.name} → {rating}★"
                    )
                )

            else:
                updated_count += 1

                self.stdout.write(
                    f"  ↻ Updated review: {username} → {product.name} → {rating}★"
                )

        # =========================================================
        # COMPLETE
        # =========================================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("========================================")
        )
        self.stdout.write(self.style.SUCCESS("     REVIEW IMPORT COMPLETED"))
        self.stdout.write(
            self.style.SUCCESS("========================================")
        )
        self.stdout.write(self.style.SUCCESS(f"✓ Reviews created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"↻ Reviews updated: {updated_count}"))
        self.stdout.write("")
