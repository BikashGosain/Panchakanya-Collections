from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from apps.wishlists.models import Wishlist

from .models import Category, Product, ProductImage

PRODUCTS_PER_PAGE = 12
CATEGORY_PRODUCTS_PER_PAGE = 6
CATEGORIES_PER_PAGE = 12


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


def apply_common_filters(products, request):
    """
    Apply search, price range, and metal type filters shared
    between product_list_view and category_view.
    """
    search_query = request.GET.get("q", "")
    if search_query:
        products = products.filter(name__icontains=search_query)

    min_price = request.GET.get("min_price", "")
    if min_price:
        products = products.filter(price__gte=min_price)

    max_price = request.GET.get("max_price", "")
    if max_price:
        products = products.filter(price__lte=max_price)

    metal_type = request.GET.get("metal", "")
    if metal_type:
        products = products.filter(metal_type=metal_type)

    filter_context = {
        "search_query": search_query,
        "min_price": min_price,
        "max_price": max_price,
        "selected_metal": metal_type,
    }

    return products, filter_context


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
    selected_category = None

    # -----------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------

    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        category_tree = get_category_and_descendants(selected_category)
        products = products.filter(category__in=category_tree)

    # -----------------------------------------
    # SHARED FILTERS (search, price, metal)
    # -----------------------------------------

    products, filter_context = apply_common_filters(products, request)

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

    expanded_category_slugs = [
        category.slug for category in selected_category_ancestors
    ]

    # -----------------------------------------
    # PAGINATION
    # -----------------------------------------

    products = products.order_by("-created_at")
    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "products/product_list.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "root_categories": root_categories,
            "metal_choices": Product.METAL_CHOICES,
            "selected_category": category_slug,
            "selected_category_obj": selected_category,
            "selected_category_ancestors": selected_category_ancestors,
            "expanded_category_slugs": expanded_category_slugs,
            **filter_context,
        },
    )


def product_detail_view(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("images"),
        slug=slug,
        status="active",
    )

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(
            user=request.user, product=product
        ).exists()

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "images": product.images.all(),
            "is_wishlisted": is_wishlisted,
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

    products, filter_context = apply_common_filters(products, request)

    paginator = Paginator(products, CATEGORY_PRODUCTS_PER_PAGE)
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
            "ancestors": ancestors,
            **filter_context,
        },
    )


def category_overview_view(request):
    categories = Category.objects.filter(parent__isnull=True).order_by("name")

    search_query = request.GET.get("q", "")
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    paginator = Paginator(categories, CATEGORIES_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "products/category_overview.html",
        {
            "root_categories": page_obj,
            "page_obj": page_obj,
            "search_query": search_query,
        },
    )
