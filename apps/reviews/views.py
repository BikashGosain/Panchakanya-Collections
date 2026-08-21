from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.products.models import Product

from .forms import ReviewForm
from .models import Review, ReviewLike
from .templatetags.reviews_tags import PAGE_SIZE, SORT_OPTIONS


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


def load_more_reviews(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    sort = request.GET.get("sort", "newest")
    if sort not in SORT_OPTIONS:
        sort = "newest"
    offset = int(request.GET.get("offset", 0))

    base_qs = Review.objects.filter(product=product, is_deleted=False).select_related(
        "user"
    )
    user_review_id = None
    if request.user.is_authenticated:
        user_review = base_qs.filter(user=request.user).first()
        user_review_id = user_review.pk if user_review else None

    others_qs = base_qs.exclude(pk=user_review_id) if user_review_id else base_qs
    others_qs = others_qs.annotate(like_count=Count("likes")).order_by(
        SORT_OPTIONS[sort]
    )

    reviews = list(others_qs[offset : offset + PAGE_SIZE])
    has_more = others_qs.count() > offset + PAGE_SIZE

    liked_review_ids = set()
    if request.user.is_authenticated:
        liked_review_ids = set(
            request.user.review_likes.filter(
                review_id__in=[r.pk for r in reviews]
            ).values_list("review_id", flat=True)
        )

    return render(
        request,
        "reviews/review_items.html",
        {
            "reviews": reviews,
            "liked_review_ids": liked_review_ids,
            "user": request.user,
            "has_more": has_more,
            "next_offset": offset + PAGE_SIZE,
            "product": product,
            "current_sort": sort,
        },
    )
