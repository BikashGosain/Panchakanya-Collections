from django import template
from django.core.paginator import Paginator
from django.db.models import Avg, Count

from ..forms import ReviewForm
from ..models import Review

register = template.Library()

SORT_OPTIONS = {
    "newest": "-created_at",
    "highest_rating": "-rating",
    "lowest_rating": "rating",
    "most_liked": "-like_count",
}


@register.inclusion_tag("reviews/review_section.html", takes_context=True)
def reviews_section(context, product):
    request = context["request"]
    sort = request.GET.get("sort", "newest")
    if sort not in SORT_OPTIONS:
        sort = "newest"

    base_qs = Review.objects.filter(product=product, is_deleted=False).select_related(
        "user"
    )
    average_rating = base_qs.aggregate(avg=Avg("rating"))["avg"]
    review_count = base_qs.count()

    reviews = base_qs.annotate(like_count=Count("likes")).order_by(SORT_OPTIONS[sort])

    user_review = None
    liked_review_ids = set()
    if request.user.is_authenticated:
        user_review = base_qs.filter(user=request.user).first()
        liked_review_ids = set(
            request.user.review_likes.filter(review__in=reviews).values_list(
                "review_id", flat=True
            )
        )
        # Exclude own review from the general list, we'll pin it separately
        reviews = reviews.exclude(pk=user_review.pk) if user_review else reviews

    page_obj = Paginator(reviews, 10).get_page(request.GET.get("review_page"))

    return {
        "product": product,
        "reviews": page_obj,
        "page_obj": page_obj,
        "average_rating": average_rating,
        "review_count": review_count,
        "user_review": user_review,
        "form": ReviewForm(),
        "liked_review_ids": liked_review_ids,
        "user": request.user,
        "current_sort": sort,
    }
