from django.contrib import admin

from .models import Review, ReviewLike


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "rating", "is_deleted", "created_at"]
    list_filter = ["rating", "is_deleted"]
    search_fields = ["user__username", "product__name", "comment"]


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "review", "created_at"]
