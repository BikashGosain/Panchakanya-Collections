from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.cart.models import Cart, CartItem
from apps.products.forms import CategoryForm, ProductForm, ProductImageFormSet
from apps.products.models import Category, Product, ProductImage
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

    product = get_object_or_404(Product.all_objects, pk=product_id)
    product.soft_delete()
    messages.success(request, f"{product.name} was deleted.")
    return redirect("dashboard:products")


@login_required
@require_POST
def dashboard_restore_product(request, product_id):
    if not request.user.is_staff:
        raise PermissionDenied

    product = get_object_or_404(Product.all_objects, pk=product_id)
    product.restore()
    messages.success(request, f"{product.name} was restored.")
    return redirect("dashboard:products")


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

    category = get_object_or_404(Category.all_objects, pk=category_id)
    category.soft_delete()
    messages.success(request, f"{category.name} was deleted.")
    return redirect("dashboard:categories")


@login_required
@require_POST
def dashboard_restore_category(request, category_id):
    if not request.user.is_staff:
        raise PermissionDenied

    category = get_object_or_404(Category.all_objects, pk=category_id)
    category.restore()
    messages.success(request, f"{category.name} was restored.")
    return redirect("dashboard:categories")
