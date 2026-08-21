from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.products.models import Product

from .forms import ReviewForm
from .models import Review, ReviewLike
from .templatetags.reviews_tags import PAGE_SIZE, SORT_OPTIONS


def get_review_section_context(request, product, sort="newest"):
    """
    Build all data required by review_section.html.
    """

    if sort not in SORT_OPTIONS:
        sort = "newest"

    base_qs = Review.objects.filter(
        product=product,
        is_deleted=False,
    ).select_related("user")

    average_rating = base_qs.aggregate(avg=Avg("rating"))["avg"]

    review_count = base_qs.count()

    user_review = None

    if request.user.is_authenticated:
        user_review = base_qs.filter(user=request.user).first()

    if user_review:
        others_qs = base_qs.exclude(pk=user_review.pk)
    else:
        others_qs = base_qs

    others_qs = others_qs.annotate(like_count=Count("likes")).order_by(
        SORT_OPTIONS[sort]
    )

    reviews = list(others_qs[:PAGE_SIZE])

    has_more = others_qs.count() > PAGE_SIZE

    liked_review_ids = set()

    if request.user.is_authenticated:
        review_ids = [review.pk for review in reviews]

        if user_review:
            review_ids.append(user_review.pk)

        liked_review_ids = set(
            request.user.review_likes.filter(review_id__in=review_ids).values_list(
                "review_id",
                flat=True,
            )
        )

    return {
        "product": product,
        "reviews": reviews,
        "average_rating": average_rating,
        "review_count": review_count,
        "user_review": user_review,
        "form": ReviewForm(instance=user_review),
        "liked_review_ids": liked_review_ids,
        "user": request.user,
        "current_sort": sort,
        "has_more": has_more,
        "next_offset": PAGE_SIZE,
    }


@login_required
@require_POST
def submit_review(request, product_id):

    product = get_object_or_404(
        Product,
        pk=product_id,
    )

    instance = Review.objects.filter(
        product=product,
        user=request.user,
    ).first()

    form = ReviewForm(
        request.POST,
        instance=instance,
    )

    if form.is_valid():
        review = form.save(commit=False)

        review.product = product
        review.user = request.user
        review.is_deleted = False

        review.save()

        return JsonResponse(
            {
                "success": True,
            }
        )

    return JsonResponse(
        {
            "success": False,
            "errors": form.errors.get_json_data(),
        },
        status=400,
    )


@login_required
@require_POST
def delete_review(request, review_id):

    review = get_object_or_404(
        Review,
        pk=review_id,
        user=request.user,
    )

    review.is_deleted = True
    review.save()

    return JsonResponse(
        {
            "success": True,
        }
    )


@login_required
@require_POST
def toggle_like(request, review_id):

    review = get_object_or_404(
        Review,
        pk=review_id,
        is_deleted=False,
    )

    like, created = ReviewLike.objects.get_or_create(
        user=request.user,
        review=review,
    )

    if not created:
        like.delete()

    return JsonResponse(
        {
            "success": True,
            "liked": created,
            "likes_count": review.likes.count(),
        }
    )


def load_more_reviews(request, product_id):

    product = get_object_or_404(
        Product,
        pk=product_id,
    )

    sort = request.GET.get(
        "sort",
        "newest",
    )

    if sort not in SORT_OPTIONS:
        sort = "newest"

    try:
        offset = int(
            request.GET.get(
                "offset",
                0,
            )
        )
    except (TypeError, ValueError):
        offset = 0

    offset = max(offset, 0)

    base_qs = Review.objects.filter(
        product=product,
        is_deleted=False,
    ).select_related("user")

    user_review_id = None

    if request.user.is_authenticated:
        user_review = base_qs.filter(user=request.user).first()

        if user_review:
            user_review_id = user_review.pk

    if user_review_id:
        others_qs = base_qs.exclude(pk=user_review_id)
    else:
        others_qs = base_qs

    others_qs = others_qs.annotate(like_count=Count("likes")).order_by(
        SORT_OPTIONS[sort]
    )

    reviews = list(others_qs[offset : offset + PAGE_SIZE])

    has_more = others_qs.count() > offset + PAGE_SIZE

    liked_review_ids = set()

    if request.user.is_authenticated and reviews:
        liked_review_ids = set(
            request.user.review_likes.filter(
                review_id__in=[review.pk for review in reviews]
            ).values_list(
                "review_id",
                flat=True,
            )
        )

    html = render(
        request,
        "reviews/review_items.html",
        {
            "reviews": reviews,
            "liked_review_ids": liked_review_ids,
            "user": request.user,
        },
    ).content.decode("utf-8")

    return JsonResponse(
        {
            "success": True,
            "html": html,
            "has_more": has_more,
            "next_offset": (offset + PAGE_SIZE),
        }
    )


def review_section(request, product_id):

    product = get_object_or_404(
        Product,
        pk=product_id,
    )

    sort = request.GET.get(
        "sort",
        "newest",
    )

    context = get_review_section_context(
        request,
        product,
        sort,
    )

    html = render(
        request,
        "reviews/review_section.html",
        context,
    ).content.decode("utf-8")

    return JsonResponse(
        {
            "success": True,
            "html": html,
        }
    )
