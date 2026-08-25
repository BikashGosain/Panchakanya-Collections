from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
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
    """
    Product listing page.

    Category behavior:
    - Selecting a parent category includes all descendant categories.
    - Selecting a child category includes that child and its descendants.
    - Only the selected category path is expanded.
    - Manually opening a parent does not automatically open all children.
    """

    # ==============================================================
    # GET PARAMETERS
    # ==============================================================

    search_query = request.GET.get("q", "").strip()

    selected_category = request.GET.get(
        "category",
        "",
    ).strip()

    selected_metal = request.GET.get(
        "metal",
        "",
    ).strip()

    min_price = request.GET.get(
        "min_price",
        "",
    ).strip()

    max_price = request.GET.get(
        "max_price",
        "",
    ).strip()

    # ==============================================================
    # BASE PRODUCT QUERY
    # ==============================================================

    products = (
        Product.objects.filter(
            status="active",
        )
        .select_related(
            "category",
        )
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(
                    is_primary=True,
                ),
                to_attr="primary_images",
            )
        )
        .order_by(
            "-created_at",
        )
    )

    # ==============================================================
    # SEARCH
    # ==============================================================

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sku__icontains=search_query)
        )

    # ==============================================================
    # CATEGORY
    # ==============================================================

    selected_category_obj = None

    selected_category_ids = set()

    descendant_category_ids = set()

    if selected_category:
        selected_category_obj = Category.objects.filter(
            slug=selected_category,
        ).first()

    if selected_category_obj:
        # ==========================================================
        # 1. FIND THE SELECTED CATEGORY + ALL PARENTS
        #
        # Used ONLY for keeping the category tree open.
        # ==========================================================

        current_category = selected_category_obj

        while current_category:
            selected_category_ids.add(
                current_category.id,
            )

            current_category = current_category.parent

        # ==========================================================
        # 2. FIND SELECTED CATEGORY + ALL DESCENDANTS
        #
        # Used for PRODUCT FILTERING.
        # ==========================================================

        categories_to_check = [
            selected_category_obj,
        ]

        while categories_to_check:
            current_category = categories_to_check.pop()

            descendant_category_ids.add(
                current_category.id,
            )

            children = list(current_category.subcategories.all())

            categories_to_check.extend(children)

        # ==========================================================
        # FILTER PRODUCTS
        # ==========================================================

        products = products.filter(
            category_id__in=descendant_category_ids,
        )

    # ==============================================================
    # METAL
    # ==============================================================

    if selected_metal:
        products = products.filter(
            metal_type=selected_metal,
        )

    # ==============================================================
    # MIN PRICE
    # ==============================================================

    if min_price:
        try:
            products = products.filter(
                price__gte=min_price,
            )

        except (
            TypeError,
            ValueError,
        ):
            pass

    # ==============================================================
    # MAX PRICE
    # ==============================================================

    if max_price:
        try:
            products = products.filter(
                price__lte=max_price,
            )

        except (
            TypeError,
            ValueError,
        ):
            pass

    # ==============================================================
    # ROOT CATEGORIES
    # ==============================================================

    root_categories = (
        Category.objects.filter(
            parent__isnull=True,
        )
        .prefetch_related(
            "subcategories",
        )
        .order_by(
            "name",
        )
    )

    # ==============================================================
    # PAGINATION
    # ==============================================================

    paginator = Paginator(
        products,
        12,
    )

    page_number = request.GET.get(
        "page",
    )

    products_page = paginator.get_page(
        page_number,
    )

    # ==============================================================
    # CONTEXT
    # ==============================================================

    context = {
        "products": products_page,
        "root_categories": root_categories,
        "selected_category": selected_category,
        "selected_category_obj": (selected_category_obj),
        # Category + all parents.
        #
        # This controls which branches are automatically
        # expanded after selecting a category.
        "selected_category_ids": (selected_category_ids),
        "search_query": search_query,
        "selected_metal": selected_metal,
        "min_price": min_price,
        "max_price": max_price,
        "metal_choices": Product.METAL_CHOICES,
    }

    return render(
        request,
        "products/product_list.html",
        context,
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
