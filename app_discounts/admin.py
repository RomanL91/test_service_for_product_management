from django.contrib import admin

from core.mixins import JsonDocumentForm
from app_discounts.models import ProductDiscount, CategoryDiscount


class BaseDiscountAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    list_display = [
        "name",
        "is_currently_active",
    ]

    def is_currently_active(self, obj):
        return obj.is_valid()

    is_currently_active.boolean = True
    is_currently_active.short_description = "Активна сейчас?"


@admin.register(ProductDiscount)
class ProductDiscountAdmin(BaseDiscountAdmin):
    filter_horizontal = ["products"]


@admin.register(CategoryDiscount)
class CategoryDiscountAdmin(BaseDiscountAdmin):
    filter_horizontal = ["categories"]
