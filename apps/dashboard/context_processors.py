from apps.cart.models import Cart
from apps.wishlists.models import Wishlist


def dashboard_counts(request):
    wishlist_count = 0
    cart_count = 0

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            cart_count = cart.items.count()

    return {
        "wishlist_count": wishlist_count,
        "cart_count": cart_count,
    }
