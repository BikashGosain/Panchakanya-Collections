from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.products.models import Product

from .forms import ReviewForm
from .models import Review, ReviewLike


@login_required
@require_POST
def submit_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    instance = Review.objects.filter(product=product, user=request.user).first()
    form = ReviewForm(request.POST, instance=instance)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.is_deleted = False
        review.save()
    return redirect("products:detail", slug=product.slug)


@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    product_slug = review.product.slug
    review.is_deleted = True
    review.save()
    return redirect("products:detail", slug=product_slug)


@login_required
@require_POST
def toggle_like(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    like, created = ReviewLike.objects.get_or_create(user=request.user, review=review)
    if not created:
        like.delete()
    return redirect("products:detail", slug=review.product.slug)
