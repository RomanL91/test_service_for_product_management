from django.db import models
from django.contrib import admin

from core.mixins import JsonDocumentForm, CustomAdminFileWidget
from app_brands.models import Brands, LogoBrand


class LogoImageInline(admin.StackedInline):
    model = LogoBrand
    max_num = 1
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}


@admin.register(Brands)
class BrandAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    list_display = [
        "name_brand",
    ]
    search_fields = [
        "name_brand",
    ]
    inlines = [
        LogoImageInline,
    ]
    fieldsets = (
        (
            "О бренде",
            {"fields": ("name_brand",)},
        ),
        (
            "Переводы на языки",
            # {"fields": (("additional_data",),), "classes": ("collapse",)},
            {"fields": ("additional_data",)},
        ),
    )
