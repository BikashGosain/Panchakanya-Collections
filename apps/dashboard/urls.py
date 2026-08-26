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
    path(
        "reviews/",
        views.reviews,
        name="reviews",
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
    path("categories/", views.dashboard_categories, name="categories"),
    path("categories/add/", views.dashboard_add_category, name="categories_add"),
    path(
        "categories/edit/<int:category_id>/",
        views.dashboard_edit_category,
        name="categories_edit",
    ),
    path(
        "categories/delete/<int:category_id>/",
        views.dashboard_delete_category,
        name="categories_delete",
    ),
    path(
        "recycle-bin/",
        views.dashboard_recycle_bin,
        name="recycle_bin",
    ),
    path(
        "recycle-bin/products/<int:product_id>/restore/",
        views.dashboard_restore_product,
        name="restore_product",
    ),
    path(
        "recycle-bin/categories/<int:category_id>/restore/",
        views.dashboard_restore_category,
        name="restore_category",
    ),
    path(
        "recycle-bin/products/restore/",
        views.dashboard_bulk_restore_products,
        name="bulk_restore_products",
    ),
    path(
        "recycle-bin/categories/restore/",
        views.dashboard_bulk_restore_categories,
        name="bulk_restore_categories",
    ),
    path(
        "recycle-bin/products/<int:product_id>/delete/",
        views.permanently_delete_product,
        name="permanently_delete_product",
    ),
    path(
        "recycle-bin/categories/<int:category_id>/delete/",
        views.permanently_delete_category,
        name="permanently_delete_category",
    ),
    path(
        "recycle-bin/products/delete/",
        views.bulk_permanently_delete_products,
        name="bulk_permanently_delete_products",
    ),
    path(
        "recycle-bin/categories/delete/",
        views.bulk_permanently_delete_categories,
        name="bulk_permanently_delete_categories",
    ),
]
