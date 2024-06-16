from django.db import models
from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin

from core.mixins import JsonDocumentForm, CustomAdminFileWidget
from app_category.models import Category, CategoryImage


class CategoryImageInline(admin.StackedInline):
    model = CategoryImage
    max_num = 1
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    form = JsonDocumentForm
    list_display = [
        "name_category",
    ]
    search_fields = [
        "name_category",
    ]
    inlines = [
        CategoryImageInline,
    ]
    fieldsets = (
        (
            "О категории",
            {"fields": ("name_category", "parent")},
        ),
        (
            "Переводы на языки",
            # {"fields": (("additional_data",),), "classes": ("collapse",)},
            {"fields": ("additional_data",)},
        ),
    )
