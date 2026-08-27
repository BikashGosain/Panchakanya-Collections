from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("health/", views.health_check, name="health"),
    path("", views.home_view, name="home"),
    path("contact/", views.contact_view, name="contact"),
]
handler404 = "apps.core.views.custom_404"
handler400 = "apps.core.views.custom_400"
handler403 = "apps.core.views.custom_403"
handler500 = "apps.core.views.custom_500"
