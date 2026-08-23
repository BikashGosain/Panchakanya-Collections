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
    path("products/", views.dashboard_products, name="products"),
    path("products/add/", views.dashboard_add_product, name="products_add"),
    path(
        "products/edit/<int:product_id>/",
        views.dashboard_edit_product,
        name="products_edit",
    ),
    path(
        "products/delete/<int:product_id>/",
        views.dashboard_delete_product,
        name="products_delete",
    ),
    path(
        "products/restore/<int:product_id>/",
        views.dashboard_restore_product,
        name="products_restore",
    ),
]
