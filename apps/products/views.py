from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list_view(request):
    products = Product.objects.filter(status="active")

    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    categories = Category.objects.all()

    return render(
        request,
        "products/product_list.html",
        {"products": products, "categories": categories},
    )


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, status="active")
    return render(request, "products/product_detail.html", {"product": product})
