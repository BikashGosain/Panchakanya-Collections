from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.products.models import Product

from .models import Cart, CartItem

# @login_required
# def cart_view(request):
#     cart, _ = Cart.objects.get_or_create(
#         user=request.user,
#     )

#     cart_items = cart.items.select_related("product").filter(
#         product__status="active",
#         product__is_deleted=False,
#     )

#     return render(
#         request,
#         "cart/cart.html",
#         {
#             "cart": cart,
#             "cart_items": cart_items,
#         },
#     )


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        status="active",
        is_deleted=False,
    )

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(quantity, 1)

    cart, _ = Cart.objects.get_or_create(
        user=request.user,
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity},
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save(update_fields=["quantity", "updated_at"])

    messages.success(
        request,
        f"{product.name} added to your cart.",
    )
    print("QUANTITY RECEIVED:", request.POST.get("quantity"))
    return redirect("products:detail", slug=product.slug)


@login_required
@require_POST
def remove_from_cart(request, product_id):
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
def update_cart(request, product_id):
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
        cart_item.save(update_fields=["quantity", "updated_at"])

        messages.success(
            request,
            f"{cart_item.product.name} quantity updated.",
        )

    return redirect("dashboard:cart")
