from django.db import models
from django.contrib import admin

from django.utils.html import format_html
from django.contrib.admin.widgets import AdminFileWidget

from django_mptt_admin.admin import DjangoMpttAdmin

from core.mixins import JsonDocumentForm
from app_category.models import Category, CategoryImage


class CustomAdminFileWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if hasattr(value, "url"):
            result.append(
                f"""<a href="{value.url}" target="_blank">
                      <img 
                        src="{value.url}" alt="{value}" 
                        width="100" height="100"
                        style="object-fit: cover;"
                      />
                    </a>"""
            )
        result.append(super().render(name, value, attrs, renderer))
        return format_html("".join(result))


class CategoryImageInline(admin.StackedInline):
    model = CategoryImage
    max_num = 10
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
        ("О категории", {"fields": ("name_category",)}),
        (
            "Переводы на языки",
            # {"fields": (("additional_data",),), "classes": ("collapse",)},
            {"fields": ("additional_data",)},
        ),
    )
