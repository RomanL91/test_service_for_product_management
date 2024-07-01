from django.contrib import admin

from app_reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "moderation",
        "rating",
    ]
    list_filter = [
        "moderation",
        "rating",
    ]
