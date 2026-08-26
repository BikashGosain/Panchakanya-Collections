from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.cart.models import Cart, CartItem
from apps.products.forms import CategoryForm, ProductForm, ProductImageFormSet
from apps.products.models import Category, Product, ProductImage
from apps.reviews.models import Review
from apps.wishlists.models import Wishlist


@login_required
def dashboard_view(request):
    return render(
        request,
        "dashboard/dashboard.html",
        {"dashboard_section": "profile"},
    )


@login_required
def dashboard_profile(request):
    return render(
        request,
        "dashboard/dashboard.html",
        {"dashboard_section": "profile"},
    )


@login_required
def dashboard_wishlist(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user,
        product__is_deleted=False,
        product__status="active",
    ).select_related("product")

    paginator = Paginator(wishlist_items, 8)

    page_number = request.GET.get("page")
    wishlist_page = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "dashboard_section": "wishlist",
            "wishlist_items": wishlist_page,
            "wishlist_page": wishlist_page,
        },
    )


@login_required
@require_POST
def dashboard_remove_wishlist(request, product_id):
    wishlist_item = get_object_or_404(
        Wishlist,
        user=request.user,
        product_id=product_id,
    )

    product_name = wishlist_item.product.name

    wishlist_item.delete()

    messages.success(
        request,
        f"{product_name} removed from your wishlist.",
    )

    return redirect("dashboard:wishlist")


@login_required
def dashboard_cart(request):
    cart, _ = Cart.objects.get_or_create(
        user=request.user,
    )

    cart_items = cart.items.select_related("product").filter(
        product__status="active",
        product__is_deleted=False,
    )

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "dashboard_section": "cart",
            "cart": cart,
            "cart_items": cart_items,
        },
    )


@login_required
@require_POST
def dashboard_remove_cart(request, product_id):
    cart = get_object_or_404(
        Cart,
        user=request.user,
    )

    cart_item = get_object_or_404(
        CartItem,
        cart=cart,
        product_id=product_id,
    )

    product_name = cart_item.product.name

    cart_item.delete()

    messages.success(
        request,
        f"{product_name} removed from your cart.",
    )

    return redirect("dashboard:cart")


@login_required
@require_POST
def dashboard_update_cart(request, product_id):
    cart = get_object_or_404(
        Cart,
        user=request.user,
    )

    cart_item = get_object_or_404(
        CartItem,
        cart=cart,
        product_id=product_id,
    )

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        cart_item.delete()

        messages.success(
            request,
            f"{cart_item.product.name} removed from your cart.",
        )
    else:
        cart_item.quantity = quantity
        cart_item.save(
            update_fields=["quantity", "updated_at"],
        )

        messages.success(
            request,
            f"{cart_item.product.name} quantity updated.",
        )

    return redirect("dashboard:cart")


@login_required
def reviews(request):
    search_query = request.GET.get("q", "").strip()

    # -------------------------
    # My Reviews
    # -------------------------
    my_reviews_qs = (
        Review.objects.filter(
            user=request.user,
            is_deleted=False,
        )
        .select_related("product")
        .annotate(like_count=Count("likes"))
        .order_by("-created_at")
    )

    if search_query:
        my_reviews_qs = my_reviews_qs.filter(
            Q(product__name__icontains=search_query)
            | Q(comment__icontains=search_query)
        )

    my_reviews_paginator = Paginator(my_reviews_qs, 5)

    my_reviews_page = request.GET.get("my_page", 1)

    my_reviews = my_reviews_paginator.get_page(my_reviews_page)

    # -------------------------
    # All Reviews for staff
    # -------------------------
    all_reviews = None

    if request.user.is_staff:
        all_reviews_qs = (
            Review.objects.filter(is_deleted=False)
            .select_related("user", "product")
            .annotate(like_count=Count("likes"))
            .order_by("-created_at")
        )

        if search_query:
            all_reviews_qs = all_reviews_qs.filter(
                Q(product__name__icontains=search_query)
                | Q(comment__icontains=search_query)
                | Q(user__username__icontains=search_query)
                | Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
            )

        all_reviews_paginator = Paginator(all_reviews_qs, 10)

        all_reviews_page = request.GET.get("all_page", 1)

        all_reviews = all_reviews_paginator.get_page(all_reviews_page)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "dashboard_section": "reviews",
            "my_reviews": my_reviews,
            "all_reviews": all_reviews,
            "search_query": search_query,
        },
    )


@login_required
def dashboard_products(request):
    if not request.user.is_staff:
        raise PermissionDenied

    products = (
        Product.all_objects.select_related("category")
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(is_primary=True),
                to_attr="cover_images",
            )
        )
        .order_by("-created_at")
    )

    search_query = request.GET.get("q", "")
    if search_query:
        products = products.filter(name__icontains=search_query) | products.filter(
            sku__icontains=search_query
        )

    category_filter = request.GET.get("category", "")
    if category_filter:
        products = products.filter(category__slug=category_filter)

    status_filter = request.GET.get("status", "")
    if status_filter:
        products = products.filter(status=status_filter)

    metal_filter = request.GET.get("metal", "")
    if metal_filter:
        products = products.filter(metal_type=metal_filter)

    featured_filter = request.GET.get("featured", "")
    if featured_filter == "yes":
        products = products.filter(featured=True)
    elif featured_filter == "no":
        products = products.filter(featured=False)

    deleted_filter = request.GET.get("deleted", "")
    if deleted_filter == "active":
        products = products.filter(is_deleted=False)
    elif deleted_filter == "deleted":
        products = products.filter(is_deleted=True)

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "dashboard_section": "products",
            "products": products_page,
            "page_obj": products_page,
            "search_query": search_query,
            "category_filter": category_filter,
            "status_filter": status_filter,
            "metal_filter": metal_filter,
            "featured_filter": featured_filter,
            "deleted_filter": deleted_filter,
            "all_categories": Category.objects.all().order_by("name"),
            "metal_choices": Product.METAL_CHOICES,
            "status_choices": Product.STATUS_CHOICES,
        },
    )


@login_required
def dashboard_add_product(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            messages.success(request, f"{product.name} was created.")
            return redirect("dashboard:products")
    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(
        request,
        "dashboard/dashboard.html",
        {"dashboard_section": "products_add", "form": form, "formset": formset},
    )


@login_required
def dashboard_edit_product(request, product_id):
    if not request.user.is_staff:
        raise PermissionDenied

    product = get_object_or_404(Product.all_objects, pk=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f"{product.name} was updated.")
            return redirect("dashboard:products")
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "dashboard_section": "products_edit",
            "form": form,
            "product": product,
            "formset": formset,
        },
    )


@login_required
@require_POST
def dashboard_delete_product(request, product_id):
    if not request.user.is_staff:
        raise PermissionDenied

    product = get_object_or_404(
        Product.all_objects,
        pk=product_id,
        is_deleted=False,
    )

    product.soft_delete()

    messages.success(
        request,
        f"{product.name} was deleted.",
    )

    return redirect("dashboard:products")


@login_required
@require_POST
def dashboard_restore_product(request, product_id):
    if not request.user.is_staff:
        raise PermissionDenied

    product = get_object_or_404(
        Product.all_objects,
        id=product_id,
        is_deleted=True,
    )

    product.restore()

    messages.success(
        request,
        f"{product.name} restored successfully.",
    )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:recycle_bin")


@login_required
def dashboard_categories(request):
    if not request.user.is_staff:
        raise PermissionDenied

    categories = Category.all_objects.select_related("parent").order_by("name")

    search_query = request.GET.get("q", "")
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    parent_filter = request.GET.get("parent", "")
    if parent_filter == "root":
        categories = categories.filter(parent__isnull=True)
    elif parent_filter == "sub":
        categories = categories.filter(parent__isnull=False)

    deleted_filter = request.GET.get("deleted", "")
    if deleted_filter == "active":
        categories = categories.filter(is_deleted=False)
    elif deleted_filter == "deleted":
        categories = categories.filter(is_deleted=True)

    show_on_home_filter = request.GET.get("show_on_home", "")
    if show_on_home_filter == "yes":
        categories = categories.filter(show_on_home=True)
    elif show_on_home_filter == "no":
        categories = categories.filter(show_on_home=False)

    paginator = Paginator(categories, 10)
    page_number = request.GET.get("page")
    categories_page = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "dashboard_section": "categories",
            "categories": categories_page,
            "page_obj": categories_page,
            "search_query": search_query,
            "parent_filter": parent_filter,
            "deleted_filter": deleted_filter,
            "show_on_home_filter": show_on_home_filter,
        },
    )


@login_required
def dashboard_add_category(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"{category.name} was created.")
            return redirect("dashboard:categories")
    else:
        form = CategoryForm()

    return render(
        request,
        "dashboard/dashboard.html",
        {"dashboard_section": "categories_add", "form": form},
    )


@login_required
def dashboard_edit_category(request, category_id):
    if not request.user.is_staff:
        raise PermissionDenied

    category = get_object_or_404(Category.all_objects, pk=category_id)

    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"{category.name} was updated.")
            return redirect("dashboard:categories")
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "dashboard/dashboard.html",
        {"dashboard_section": "categories_edit", "form": form, "category": category},
    )


@login_required
@require_POST
def dashboard_delete_category(request, category_id):
    if not request.user.is_staff:
        raise PermissionDenied

    category = get_object_or_404(
        Category.all_objects,
        pk=category_id,
        is_deleted=False,
    )

    # Prevent deleting a category that still has active children.
    child_count = category.subcategories.filter(
        is_deleted=False,
    ).count()

    if child_count > 0:
        messages.error(
            request,
            f"Cannot delete {category.name} because it has "
            f"{child_count} active subcategor"
            f"{'y' if child_count == 1 else 'ies'}. "
            "Delete or move the subcategories first.",
        )
        return redirect("dashboard:categories")

    # Prevent deleting a category containing active products.
    total_product_count = category.product_count

    if total_product_count > 0:
        messages.error(
            request,
            f"Cannot delete {category.name} — it still has "
            f"{total_product_count} active product"
            f"{'s' if total_product_count != 1 else ''}. "
            "Move or delete those products first.",
        )
        return redirect("dashboard:categories")

    category.soft_delete()

    messages.success(
        request,
        f"{category.name} was deleted.",
    )

    return redirect("dashboard:categories")


@login_required
@require_POST
def dashboard_restore_category(request, category_id):
    if not request.user.is_staff:
        raise PermissionDenied

    category = get_object_or_404(
        Category.all_objects,
        id=category_id,
        is_deleted=True,
    )

    try:
        category.restore()
    except ValidationError as exc:
        messages.error(
            request,
            exc.message,
        )
        return redirect("dashboard:recycle_bin")

    messages.success(
        request,
        f"{category.name} was restored.",
    )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:recycle_bin")


@login_required
def dashboard_recycle_bin(request):
    if not request.user.is_staff:
        raise PermissionDenied

    deleted_products = (
        Product.all_objects.filter(is_deleted=True)
        .select_related("category")
        .prefetch_related("images")
        .order_by("-deleted_at")
    )

    deleted_categories = (
        Category.all_objects.filter(is_deleted=True)
        .select_related("parent")
        .order_by("-deleted_at")
    )

    # Products and categories have completely independent pagination.
    product_paginator = Paginator(deleted_products, 10)
    category_paginator = Paginator(deleted_categories, 10)

    product_page_number = request.GET.get("product_page", 1)
    category_page_number = request.GET.get("category_page", 1)

    products_page = product_paginator.get_page(product_page_number)
    categories_page = category_paginator.get_page(category_page_number)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "dashboard_section": "recycle_bin",
            "deleted_products": products_page,
            "deleted_categories": categories_page,
            "product_page": products_page,
            "category_page": categories_page,
        },
    )


@login_required
@require_POST
def dashboard_bulk_restore_products(request):
    if not request.user.is_staff:
        raise PermissionDenied

    product_ids = request.POST.getlist("product_ids")

    products = Product.all_objects.filter(
        id__in=product_ids,
        is_deleted=True,
    )

    restored_count = products.update(
        is_deleted=False,
        deleted_at=None,
    )

    messages.success(
        request,
        f"{restored_count} product(s) restored successfully.",
    )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:recycle_bin")


@login_required
@require_POST
def dashboard_bulk_restore_categories(request):
    if not request.user.is_staff:
        raise PermissionDenied

    category_ids = request.POST.getlist("category_ids")

    categories = Category.all_objects.filter(
        id__in=category_ids,
        is_deleted=True,
    ).select_related("parent")

    restored_count = 0
    skipped_count = 0

    for category in categories:
        try:
            category.restore()
        except ValidationError:
            skipped_count += 1
        else:
            restored_count += 1

    if restored_count:
        messages.success(
            request,
            f"{restored_count} categor"
            f"{'y' if restored_count == 1 else 'ies'} restored successfully.",
        )

    if skipped_count:
        messages.warning(
            request,
            f"{skipped_count} categor"
            f"{'y' if skipped_count == 1 else 'ies'} could not be restored "
            "because their parent category is deleted. Restore the parent first.",
        )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:recycle_bin")


@login_required
@require_POST
def permanently_delete_product(request, product_id):
    if not request.user.is_staff:
        raise PermissionDenied

    product = get_object_or_404(
        Product.all_objects,
        id=product_id,
        is_deleted=True,
    )

    product_name = product.name
    product.delete()

    messages.success(
        request,
        f"{product_name} permanently deleted.",
    )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:recycle_bin")


@login_required
@require_POST
def permanently_delete_category(request, category_id):
    if not request.user.is_staff:
        raise PermissionDenied

    category = get_object_or_404(
        Category.all_objects,
        id=category_id,
        is_deleted=True,
    )

    category_name = category.name

    try:
        category.delete()
    except ProtectedError:
        messages.error(
            request,
            f"Cannot permanently delete {category_name} because "
            "it has subcategories. Permanently delete the subcategories first.",
        )
        return redirect("dashboard:recycle_bin")

    messages.success(
        request,
        f"{category_name} permanently deleted.",
    )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:recycle_bin")


@login_required
@require_POST
def bulk_permanently_delete_products(request):
    if not request.user.is_staff:
        raise PermissionDenied

    product_ids = request.POST.getlist("product_ids")

    products = Product.all_objects.filter(
        id__in=product_ids,
        is_deleted=True,
    )

    deleted_count = products.count()

    products.delete()

    messages.success(
        request,
        f"{deleted_count} product(s) permanently deleted.",
    )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:recycle_bin")


@login_required
@require_POST
def bulk_permanently_delete_categories(request):
    if not request.user.is_staff:
        raise PermissionDenied

    category_ids = request.POST.getlist("category_ids")

    categories = Category.all_objects.filter(
        id__in=category_ids,
        is_deleted=True,
    )

    deleted_count = categories.count()

    categories.delete()

    messages.success(
        request,
        f"{deleted_count} categor(ies) permanently deleted.",
    )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:recycle_bin")
