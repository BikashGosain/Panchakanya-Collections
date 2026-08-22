from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_view, name="home"),
    path("profile/", views.dashboard_profile, name="profile"),
    path("wishlist/", views.dashboard_wishlist, name="wishlist"),
    path(
        "wishlist/remove/<int:product_id>/",
        views.dashboard_remove_wishlist,
        name="wishlist_remove",
    ),
    path("cart/", views.dashboard_cart, name="cart"),
    path(
        "cart/remove/<int:product_id>/", views.dashboard_remove_cart, name="cart_remove"
    ),
    path(
        "cart/update/<int:product_id>/", views.dashboard_update_cart, name="cart_update"
    ),
]
