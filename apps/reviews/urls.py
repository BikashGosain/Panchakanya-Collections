from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("submit/<int:product_id>/", views.submit_review, name="submit"),
    path("delete/<int:review_id>/", views.delete_review, name="delete"),
    path("like/<int:review_id>/", views.toggle_like, name="toggle_like"),
    path("load-more/<int:product_id>/", views.load_more_reviews, name="load_more"),
]
