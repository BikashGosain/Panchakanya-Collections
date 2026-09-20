from django.db import migrations


def create_trigram_indexes(apps, schema_editor):
    # pg_trgm is PostgreSQL-only. Skip on any other database (for example
    # SQLite, which your CI uses) so `migrate` still works there.
    if schema_editor.connection.vendor != "postgresql":
        return

    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    schema_editor.execute(
        "CREATE INDEX IF NOT EXISTS idx_product_name_trgm "
        "ON products_product USING gin (name gin_trgm_ops)"
    )
    schema_editor.execute(
        "CREATE INDEX IF NOT EXISTS idx_product_sku_trgm "
        "ON products_product USING gin (sku gin_trgm_ops)"
    )


def drop_trigram_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    schema_editor.execute("DROP INDEX IF EXISTS idx_product_sku_trgm")
    schema_editor.execute("DROP INDEX IF EXISTS idx_product_name_trgm")


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0008_product_indexes"),
    ]

    operations = [
        migrations.RunPython(create_trigram_indexes, drop_trigram_indexes),
    ]
