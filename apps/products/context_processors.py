from django.db.models import Count, Q

from .models import Category


def header_categories(request):
    categories = (
        Category.objects.annotate(
            active_product_count=Count(
                "products",
                filter=Q(
                    products__status="active",
                    products__is_deleted=False,
                ),
            )
        )
        .filter(active_product_count__gt=0)
        .order_by("-active_product_count", "name")[:4]
    )

    return {
        "header_categories": categories,
    }
