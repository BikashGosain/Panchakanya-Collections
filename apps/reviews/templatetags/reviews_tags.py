from django import template
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


PAGE_SIZE = 5


@register.inclusion_tag(
    "reviews/review_section.html",
    takes_context=True,
)
def reviews_section(context, product):

    request = context["request"]

    sort = request.GET.get(
        "sort",
        "newest",
    )

    if sort not in SORT_OPTIONS:
        sort = "newest"

    base_qs = Review.objects.filter(
        product=product,
        is_deleted=False,
    ).select_related("user")

    average_rating = base_qs.aggregate(avg=Avg("rating"))["avg"]

    review_count = base_qs.count()

    user_review = None
    liked_review_ids = set()

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

    if request.user.is_authenticated:
        visible_ids = [review.pk for review in reviews]

        if user_review:
            visible_ids.append(user_review.pk)

        liked_review_ids = set(
            request.user.review_likes.filter(review_id__in=visible_ids).values_list(
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
        "form": ReviewForm(),
        "liked_review_ids": liked_review_ids,
        "user": request.user,
        "current_sort": sort,
        "has_more": has_more,
        "next_offset": PAGE_SIZE,
    }
