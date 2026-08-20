from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list_view, name="list"),
    path("categories/", views.category_overview_view, name="category_overview"),
    path("category/<slug:slug>/", views.category_view, name="category"),
    path("<slug:slug>/", views.product_detail_view, name="detail"),
]
