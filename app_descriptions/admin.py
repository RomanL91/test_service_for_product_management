from django.db import models
from django.contrib import admin

from flat_json_widget.widgets import FlatJsonWidget

from core.mixins import JsonDocumentForm
from app_descriptions.models import ProductDescription


class ProductDescriptionFieldsets:
    fieldsets = (
        (
            "Выбор продукта",
            {"fields": ("product",)},
        ),
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


class ProductDescriptionInline(admin.StackedInline, ProductDescriptionFieldsets):
    model = ProductDescription
    max_num = 1
    extra = 0
    formfield_overrides = {models.JSONField: {"widget": FlatJsonWidget}}
    fieldsets = ProductDescriptionFieldsets.fieldsets


@admin.register(ProductDescription)
class ProductDescriptionAdmin(admin.ModelAdmin, ProductDescriptionFieldsets):
    form = JsonDocumentForm
    autocomplete_fields = [
        "product",
    ]
    fieldsets = ProductDescriptionFieldsets.fieldsets
