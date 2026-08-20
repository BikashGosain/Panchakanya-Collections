from django.contrib import admin

from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "show_on_home"]
    list_filter = ["show_on_home"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj is not None:
            # Start with all categories.
            parent_field = form.base_fields["parent"]

            # Categories that cannot be selected as parents.
            invalid_ids = {obj.pk}

            # Find all descendants of the current category.
            descendants = self.get_descendants(obj)

            invalid_ids.update(category.pk for category in descendants)

            # Remove the current category and all descendants.
            parent_field.queryset = Category.objects.exclude(pk__in=invalid_ids)

        return form

    def get_descendants(self, category):
        descendants = []

        for child in category.subcategories.all():
            descendants.append(child)

            descendants.extend(self.get_descendants(child))

        return descendants


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "metal_type",
        "price",
        "stock",
        "status",
        "featured",
    ]

    list_filter = [
        "category",
        "metal_type",
        "status",
        "featured",
    ]

    search_fields = [
        "name",
        "sku",
    ]

    inlines = [ProductImageInline]
