from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.products.models import Product


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="one_review_per_user_per_product"
            ),
        ]
        ordering = ["-created_at"]

        indexes = [
            # Product page review list: newest first, hiding deleted reviews.
            models.Index(
                fields=["product", "-created_at"],
                condition=Q(is_deleted=False),
                name="idx_review_product_live",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}★"


class ReviewLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_likes"
    )
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "review"], name="one_like_per_user_per_review"
            ),
        ]

    def __str__(self):
        return f"{self.user.username} likes review #{self.review_id}"


class ProductRatingSummary(models.Model):
    """
    Pre-computed rating statistics for one product (one row per product).

    Written only by PostgreSQL triggers, never by Python code, so it always
    matches the reviews table no matter how a review was changed.
    """

    product = models.OneToOneField(
        "products.Product",
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="rating_summary",
    )

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
    )

    review_count = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "product rating summaries"

    def __str__(self):
        return f"{self.product_id}: {self.average_rating} ({self.review_count})"
