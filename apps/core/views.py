from django.shortcuts import render

from apps.products.models import Product


def home_view(request):
    featured_products = Product.objects.filter(status="active", featured=True)[:8]
    latest_products = Product.objects.filter(status="active").order_by("-created_at")[
        :8
    ]

    return render(
        request,
        "core/home.html",
        {"featured_products": featured_products, "latest_products": latest_products},
    )
