from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.cart.models import Cart, CartItem
from apps.products.forms import ProductForm, ProductImageFormSet
from apps.products.models import Product, ProductImage
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
