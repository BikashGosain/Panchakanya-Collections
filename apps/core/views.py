from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import render

from apps.products.models import Category, Product, ProductImage


def home_view(request):
    featured_qs = Product.objects.filter(
        status="active", featured=True
    ).prefetch_related(
        Prefetch(
            "images",
            queryset=ProductImage.objects.filter(is_primary=True),
            to_attr="cover_images",
        )
    )
    featured_search = request.GET.get("featured_q", "")
    if featured_search:
        featured_qs = featured_qs.filter(name__icontains=featured_search)
    featured_paginator = Paginator(featured_qs, 6)
    featured_page_obj = featured_paginator.get_page(request.GET.get("featured_page"))

    category_qs = Category.objects.filter(show_on_home=True).order_by("name")
    category_search = request.GET.get("cat_q", "")
    if category_search:
        category_qs = category_qs.filter(name__icontains=category_search)
    category_paginator = Paginator(category_qs, 4)
    category_page_obj = category_paginator.get_page(request.GET.get("cat_page"))

    return render(
        request,
        "core/home.html",
        {
            "featured_products": featured_page_obj,
            "featured_page_obj": featured_page_obj,
            "featured_search": featured_search,
            "root_categories": category_page_obj,
            "category_page_obj": category_page_obj,
            "category_search": category_search,
        },
    )
