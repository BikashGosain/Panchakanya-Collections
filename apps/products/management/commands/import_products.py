import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.products.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = "Import categories, products, and product images from CSV files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="csv_data/products",
            help="Directory containing the CSV files.",
        )

    # =============================================================
    # CSV HELPERS
    # =============================================================

    def clean_row(self, row):
        """
        Clean CSV column names and values.

        Handles:
        - UTF-8 BOM
        - accidental spaces
        - empty values
        """
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
        """
        Read CSV and validate required columns.
        """

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

                # Clean header names
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

                for line_number, row in enumerate(
                    reader,
                    start=2,
                ):
                    cleaned_row = self.clean_row(row)

                    # Ignore completely empty rows
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

        categories_file = csv_dir / "categories.csv"
        products_file = csv_dir / "products.csv"
        images_file = csv_dir / "product_images.csv"

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("========================================")
        )
        self.stdout.write(self.style.SUCCESS("       PRODUCT CSV IMPORT"))
        self.stdout.write(
            self.style.SUCCESS("========================================")
        )
        self.stdout.write("")

        # =========================================================
        # 1. CATEGORIES
        # =========================================================

        self.stdout.write(self.style.WARNING("Importing categories..."))

        category_rows = self.read_csv(
            categories_file,
            [
                "id",
                "name",
                "slug",
                "parent_id",
            ],
        )

        remaining_categories = category_rows.copy()

        while remaining_categories:
            imported_this_round = False

            for row in remaining_categories[:]:
                line_number = row["_line_number"]

                # -------------------------------------------------
                # Validate ID
                # -------------------------------------------------

                try:
                    category_id = int(row["id"])
                except ValueError:
                    raise CommandError(
                        f"Invalid category ID on line {line_number}: {row['id']}"
                    )

                # -------------------------------------------------
                # Validate parent
                # -------------------------------------------------

                parent_id = row["parent_id"]

                if parent_id:
                    try:
                        parent_id = int(parent_id)
                    except ValueError:
                        raise CommandError(
                            f"Invalid parent_id on line "
                            f"{line_number}: {row['parent_id']}"
                        )

                    # Parent doesn't exist yet.
                    # Try it again on the next round.
                    if not Category.objects.filter(pk=parent_id).exists():
                        continue

                else:
                    parent_id = None

                # -------------------------------------------------
                # Create / update category
                # -------------------------------------------------

                category, created = Category.objects.update_or_create(
                    pk=category_id,
                    defaults={
                        "name": row["name"],
                        "slug": row["slug"],
                        "parent_id": parent_id,
                    },
                )

                remaining_categories.remove(row)
                imported_this_round = True

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Created category: {category.name}")
                    )
                else:
                    self.stdout.write(f"  ↻ Updated category: {category.name}")

            # -----------------------------------------------------
            # Prevent infinite loop
            # -----------------------------------------------------

            if not imported_this_round:
                unresolved = []

                for row in remaining_categories:
                    unresolved.append(
                        f"ID {row['id']} ({row['name']}) → parent_id={row['parent_id']}"
                    )

                raise CommandError(
                    "\nCould not resolve category "
                    "parent relationships.\n\n"
                    "Problem categories:\n" + "\n".join(unresolved)
                )

        self.stdout.write(
            self.style.SUCCESS(f"✓ Categories imported: {len(category_rows)}")
        )

        # =========================================================
        # 2. PRODUCTS
        # =========================================================

        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Importing products..."))

        product_rows = self.read_csv(
            products_file,
            [
                "id",
                "name",
                "slug",
                "sku",
                "description",
                "category_id",
                "metal_type",
                "purity",
                "weight_grams",
                "price",
                "stock",
                "status",
                "featured",
            ],
        )

        for row in product_rows:
            line_number = row["_line_number"]

            # -----------------------------------------------------
            # Product ID
            # -----------------------------------------------------

            try:
                int(row["id"])
            except ValueError:
                raise CommandError(
                    f"Invalid product ID on line {line_number}: {row['id']}"
                )

            # -----------------------------------------------------
            # Category ID
            # -----------------------------------------------------

            try:
                category_id = int(row["category_id"])
            except ValueError:
                raise CommandError(
                    f"Invalid category_id on line {line_number}: {row['category_id']}"
                )

            if not Category.objects.filter(pk=category_id).exists():
                raise CommandError(
                    f"Category ID {category_id} does not exist "
                    f"for product '{row['name']}' "
                    f"on line {line_number}."
                )

            # -----------------------------------------------------
            # Metal type
            # -----------------------------------------------------

            allowed_metals = {
                "gold",
                "silver",
                "diamond",
                "platinum",
            }

            if row["metal_type"] not in allowed_metals:
                raise CommandError(
                    f"Invalid metal_type "
                    f"'{row['metal_type']}' "
                    f"for product '{row['name']}'.\n\n"
                    f"Allowed values: "
                    f"{', '.join(sorted(allowed_metals))}"
                )

            # -----------------------------------------------------
            # Status
            # -----------------------------------------------------

            allowed_statuses = {
                "active",
                "inactive",
            }

            if row["status"] not in allowed_statuses:
                raise CommandError(
                    f"Invalid status "
                    f"'{row['status']}' "
                    f"for product '{row['name']}'.\n\n"
                    f"Allowed values: "
                    f"active, inactive"
                )

            # -----------------------------------------------------
            # Stock
            # -----------------------------------------------------

            try:
                stock = int(row["stock"])
            except ValueError:
                raise CommandError(
                    f"Invalid stock for product "
                    f"'{row['name']}' "
                    f"on line {line_number}: "
                    f"{row['stock']}"
                )

            # -----------------------------------------------------
            # Featured
            # -----------------------------------------------------

            featured = row["featured"].lower() in {
                "true",
                "1",
                "yes",
            }

            # -----------------------------------------------------
            # Weight
            # -----------------------------------------------------

            weight_grams = row["weight_grams"] if row["weight_grams"] else None

            # -----------------------------------------------------
            # Create / update product
            # -----------------------------------------------------

            existing_product = Product.objects.filter(sku=row["sku"]).first()

            if existing_product:
                product = existing_product

                product.name = row["name"]
                product.slug = row["slug"]
                product.description = row["description"]
                product.category_id = category_id
                product.metal_type = row["metal_type"]
                product.purity = row["purity"]
                product.weight_grams = weight_grams
                product.price = row["price"]
                product.stock = stock
                product.status = row["status"]
                product.featured = featured

                product.save()

                created = False

            else:
                product = Product(
                    name=row["name"],
                    slug=row["slug"],
                    sku=row["sku"],
                    description=row["description"],
                    category_id=category_id,
                    metal_type=row["metal_type"],
                    purity=row["purity"],
                    weight_grams=weight_grams,
                    price=row["price"],
                    stock=stock,
                    status=row["status"],
                    featured=featured,
                )

                product.save()

                created = True

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Created product: {product.name}")
                )
            else:
                self.stdout.write(f"  ↻ Updated product: {product.name}")

        self.stdout.write(
            self.style.SUCCESS(f"✓ Products imported: {len(product_rows)}")
        )

        # =========================================================
        # 3. PRODUCT IMAGES
        # =========================================================
        # =========================================================
        # 3. PRODUCT IMAGES
        # =========================================================

        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Importing product images..."))

        image_rows = self.read_csv(
            images_file,
            [
                "id",
                "product_id",
                "image",
                "is_primary",
            ],
        )

        # ---------------------------------------------------------
        # Build CSV product ID -> actual Django Product mapping
        # ---------------------------------------------------------

        product_rows_by_csv_id = {}

        for row in product_rows:
            csv_product_id = int(row["id"])
            sku = row["sku"]

            product = Product.objects.filter(sku=sku).first()

            if product is None:
                raise CommandError(
                    f"Could not find product with SKU "
                    f"'{sku}' for CSV product ID "
                    f"{csv_product_id}."
                )

            product_rows_by_csv_id[csv_product_id] = product

        # ---------------------------------------------------------
        # Import images
        # ---------------------------------------------------------

        for row in image_rows:
            line_number = row["_line_number"]

            try:
                image_id = int(row["id"])
            except ValueError:
                raise CommandError(
                    f"Invalid image ID on line {line_number}: {row['id']}"
                )

            try:
                csv_product_id = int(row["product_id"])
            except ValueError:
                raise CommandError(
                    f"Invalid product_id on line {line_number}: {row['product_id']}"
                )

            # Find the actual Django Product using
            # the product ID from products.csv.
            product = product_rows_by_csv_id.get(csv_product_id)

            if product is None:
                raise CommandError(
                    f"Product CSV ID {csv_product_id} "
                    f"does not exist in products.csv "
                    f"for image '{row['image']}' "
                    f"on line {line_number}."
                )

            is_primary = row["is_primary"].lower() in {
                "true",
                "1",
                "yes",
            }

            _, created = ProductImage.objects.update_or_create(
                pk=image_id,
                defaults={
                    "product": product,
                    "image": row["image"],
                    "is_primary": is_primary,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Added image: {product.name} → {row['image']}"
                    )
                )
            else:
                self.stdout.write(f"  ↻ Updated image: {product.name} → {row['image']}")

        self.stdout.write(
            self.style.SUCCESS(f"✓ Product images imported: {len(image_rows)}")
        )

        # =========================================================
        # COMPLETE
        # =========================================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("========================================")
        )
        self.stdout.write(self.style.SUCCESS("     IMPORT COMPLETED SUCCESSFULLY"))
        self.stdout.write(
            self.style.SUCCESS("========================================")
        )
        self.stdout.write("")
