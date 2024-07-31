from django.db import models
from django.contrib import admin

from core.mixins import JsonDocumentForm, CustomAdminFileWidget
from app_descriptions.models import ProductDescription, DescriptionImage


class ProductDescriptionFieldsets:
    fieldsets = (
        (
            "Описание Заголовок",
            {
                "fields": (
                    "title_description",
                    "additional_data",
                )
            },
        ),
        (
            "Описание Тело",
            {
                "fields": (
                    "body_description",
                    "additional_data_to_desc",
                )
            },
        ),
    )


class DescriptionImageInline(admin.StackedInline):
    model = DescriptionImage
    max_num = 10
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}


@admin.register(ProductDescription)
class ProductDescriptionAdmin(admin.ModelAdmin, ProductDescriptionFieldsets):
    form = JsonDocumentForm
    fieldsets = ProductDescriptionFieldsets.fieldsets
    inlines = [
        DescriptionImageInline,
    ]
    search_fields = [
        "title_description",
    ]
