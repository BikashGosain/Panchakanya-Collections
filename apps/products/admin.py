from django.contrib import admin
from django.utils import timezone

from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


def soft_delete_action(modeladmin, request, queryset):
    queryset.update(is_deleted=True, deleted_at=timezone.now())


@admin.action(description="Restore selected items")
def restore_action(modeladmin, request, queryset):
    queryset.update(is_deleted=False, deleted_at=None)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "show_on_home", "is_deleted"]
    list_filter = ["show_on_home", "is_deleted"]
    actions = [soft_delete_action, restore_action]

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
        "is_deleted",
    ]

    list_filter = [
        "category",
        "metal_type",
        "status",
        "featured",
        "is_deleted",
    ]

    search_fields = [
        "name",
        "sku",
    ]

    inlines = [ProductImageInline]
    actions = [soft_delete_action, restore_action]

    def get_queryset(self, request):
        return Product.all_objects.all()
