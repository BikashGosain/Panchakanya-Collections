from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import JsonResponse

# from django.conf import settings
# from django.core.mail import EmailMessage
from django.shortcuts import render

# from .forms import ContactForm
from apps.products.models import Category, Product, ProductImage


def home_view(request):
    featured_qs = Product.objects.filter(
        status="active", featured=True
    ).prefetch_related(
        Prefetch(
            "images",
            queryset=ProductImage.objects.filter(is_primary=True),
            to_attr="cover_images",
        )
    )
    featured_search = request.GET.get("featured_q", "")
    if featured_search:
        featured_qs = featured_qs.filter(name__icontains=featured_search)
    featured_paginator = Paginator(featured_qs, 6)
    featured_page_obj = featured_paginator.get_page(request.GET.get("featured_page"))

    category_qs = Category.objects.filter(show_on_home=True).order_by("name")
    category_search = request.GET.get("cat_q", "")
    if category_search:
        category_qs = category_qs.filter(name__icontains=category_search)
    category_paginator = Paginator(category_qs, 4)
    category_page_obj = category_paginator.get_page(request.GET.get("cat_page"))

    return render(
        request,
        "core/home.html",
        {
            "featured_products": featured_page_obj,
            "featured_page_obj": featured_page_obj,
            "featured_search": featured_search,
            "root_categories": category_page_obj,
            "category_page_obj": category_page_obj,
            "category_search": category_search,
        },
    )


# def contact_view(request):
#     if request.method == "POST":
#         form = ContactForm(request.POST)

#         if form.is_valid():
#             name = form.cleaned_data["name"]
#             email = form.cleaned_data["email"]
#             phone = form.cleaned_data["phone"]
#             message = form.cleaned_data["message"]

#             email_message = EmailMessage(
#                 subject=f"Contact Form: Message from {name}",
#                 body=(
#                     f"Name: {name}\n"
#                     f"Email: {email}\n"
#                     f"Phone: {phone or 'Not provided'}\n\n"
#                     f"Message:\n{message}"
#                 ),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 to=[settings.DEFAULT_FROM_EMAIL],
#                 reply_to=[email],
#             )

#             email_message.send(fail_silently=False)

#             return redirect("core:contact")

#     else:
#         form = ContactForm()

#     return render(
#         request,
#         "core/contact.html",
#         {"form": form},
#     )


def contact_view(request):
    return render(request, "core/contact.html")


def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_400(request, exception):
    return render(request, "400.html", status=400)


def custom_403(request, exception):
    return render(request, "403.html", status=403)


def custom_500(request):
    return render(request, "500.html", status=500)


def health_check(request):
    return JsonResponse({"status": "ok"})
