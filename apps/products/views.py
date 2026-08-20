from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from .models import Category, Product, ProductImage


def get_category_and_descendants(category):
    """
    Return the selected category and all of its descendants.
    """
    categories = [category]

    for child in category.subcategories.all():
        categories.extend(get_category_and_descendants(child))

    return categories


def get_category_ancestors(category):
    """
    Return all ancestors of the selected category,
    from root to immediate parent.
    """
    ancestors = []

    parent = category.parent

    while parent is not None:
        ancestors.append(parent)
        parent = parent.parent

    ancestors.reverse()

    return ancestors


def product_list_view(request):
    products = (
        Product.objects.filter(status="active")
        .select_related("category")
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(is_primary=True),
                to_attr="cover_images",
            )
        )
    )

    category_slug = request.GET.get("category", "")
    search_query = request.GET.get("q", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    metal_type = request.GET.get("metal", "")

    selected_category = None

    # -----------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------

    if category_slug:
        selected_category = get_object_or_404(
            Category,
            slug=category_slug,
        )

        category_tree = get_category_and_descendants(selected_category)

        products = products.filter(category__in=category_tree)

    # -----------------------------------------
    # SEARCH FILTER
    # -----------------------------------------

    if search_query:
        products = products.filter(name__icontains=search_query)

    # -----------------------------------------
    # MIN PRICE
    # -----------------------------------------

    if min_price:
        products = products.filter(price__gte=min_price)

    # -----------------------------------------
    # MAX PRICE
    # -----------------------------------------

    if max_price:
        products = products.filter(price__lte=max_price)

    # -----------------------------------------
    # METAL FILTER
    # -----------------------------------------

    if metal_type:
        products = products.filter(metal_type=metal_type)

    # -----------------------------------------
    # ROOT CATEGORIES
    # -----------------------------------------

    root_categories = (
        Category.objects.filter(parent__isnull=True)
        .prefetch_related("subcategories")
        .order_by("name")
    )

    # -----------------------------------------
    # SELECTED CATEGORY ANCESTORS
    # -----------------------------------------

    selected_category_ancestors = []

    if selected_category:
        selected_category_ancestors = get_category_ancestors(selected_category)

    # -----------------------------------------
    # CATEGORIES THAT SHOULD BE OPEN
    # -----------------------------------------

    expanded_category_slugs = [
        category.slug for category in selected_category_ancestors
    ]

    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    products = products.order_by("-created_at")

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "products/product_list.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "root_categories": root_categories,
            "metal_choices": Product.METAL_CHOICES,
            "search_query": search_query,
            "min_price": min_price,
            "max_price": max_price,
            "selected_metal": metal_type,
            "selected_category": category_slug,
            "selected_category_obj": selected_category,
            "selected_category_ancestors": selected_category_ancestors,
            "expanded_category_slugs": expanded_category_slugs,
        },
    )


def product_detail_view(request, slug):

    product = get_object_or_404(
        Product.objects.prefetch_related("images"),
        slug=slug,
        status="active",
    )

    images = list(product.images.all())

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "images": images,
        },
    )


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    subcategories = category.subcategories.all()

    category_tree = get_category_and_descendants(category)
    products = (
        Product.objects.filter(status="active", category__in=category_tree)
        .select_related("category")
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(is_primary=True),
                to_attr="cover_images",
            )
        )
    )

    search_query = request.GET.get("q", "")
    if search_query:
        products = products.filter(name__icontains=search_query)

    paginator = Paginator(products, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    ancestors = get_category_ancestors(category)

    return render(
        request,
        "products/category_detail.html",
        {
            "category": category,
            "subcategories": subcategories,
            "products": page_obj,
            "page_obj": page_obj,
            "search_query": search_query,
            "ancestors": ancestors,
        },
    )


def category_overview_view(request):
    categories = Category.objects.filter(parent__isnull=True).order_by("name")

    search_query = request.GET.get("q", "")
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    paginator = Paginator(categories, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "products/category_overview.html",
        {
            "root_categories": page_obj,
            "page_obj": page_obj,
            "search_query": search_query,
        },
    )
