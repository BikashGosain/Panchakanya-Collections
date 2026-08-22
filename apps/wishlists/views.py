from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.products.models import Product

from .models import Wishlist


@login_required
@require_POST
def add_to_wishlist(
    request,
    product_id,
    status="active",
):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_deleted=False,
    )

    _, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
    )

    if created:
        messages.success(
            request,
            f"{product.name} added to your wishlist.",
        )
    else:
        messages.info(
            request,
            f"{product.name} is already in your wishlist.",
        )

    return redirect("products:detail", slug=product.slug)


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    wishlist_item = get_object_or_404(
        Wishlist,
        user=request.user,
        product_id=product_id,
    )

    product_name = wishlist_item.product.name
    product_slug = wishlist_item.product.slug

    wishlist_item.delete()

    messages.success(
        request,
        f"{product_name} removed from your wishlist.",
    )

    return redirect("products:detail", slug=product_slug)


# @login_required
# def wishlist_view(request):
#     wishlist_items = Wishlist.objects.filter(
#         user=request.user,
#         product__is_deleted=False,
#         product__status="active",
#     ).select_related("product")

#     return render(
#         request,
#         "wishlists/wishlist.html",
#         {"wishlist_items": wishlist_items},
#     )
