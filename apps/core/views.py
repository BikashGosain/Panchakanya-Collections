from django.db.models import Prefetch
from django.shortcuts import render

from apps.products.models import Category, Product, ProductImage


def home_view(request):
    featured_products = Product.objects.filter(
        status="active", featured=True
    ).prefetch_related(
        Prefetch(
            "images",
            queryset=ProductImage.objects.filter(is_primary=True),
            to_attr="cover_images",
        )
    )[:6]
    home_categories = Category.objects.filter(show_on_home=True).order_by("name")[:4]

    return render(
        request,
        "core/home.html",
        {"featured_products": featured_products, "root_categories": home_categories},
    )
