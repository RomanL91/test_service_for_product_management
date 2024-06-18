from django.db import models
from django.contrib import admin

from flat_json_widget.widgets import FlatJsonWidget

from core.mixins import JsonDocumentForm
from app_specifications.models import (
    Specifications,
    NameSpecifications,
    ValueSpecifications,
)


class SpecificationsInline(admin.StackedInline):
    model = Specifications
    max_num = 100
    extra = 0
    autocomplete_fields = ["value_specification"]
    formfield_overrides = {models.JSONField: {"widget": FlatJsonWidget}}


@admin.register(Specifications)
class SpecificationAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    list_display = [
        "name_specification",
    ]
    search_fields = [
        "name_specification",
    ]
    autocomplete_fields = [
        "product",
        "name_specification",
        "value_specification",
    ]
    fieldsets = (
        (
            "Характеристика",
            {
                "fields": (
                    "name_specification",
                    "value_specification",
                    "product",
                )
            },
        ),
    )


@admin.register(NameSpecifications)
class NameSpecificationsAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    list_display = [
        "name_specification",
    ]
    search_fields = [
        "name_specification",
    ]
    fieldsets = (
        (
            "Название Характеристики",
            {"fields": ("name_specification",)},
        ),
        (
            "Переводы на языки",
            {"fields": ("additional_data",)},
        ),
    )


@admin.register(ValueSpecifications)
class ValueSpecificationsAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    list_display = [
        "value_specification",
    ]
    search_fields = [
        "value_specification",
    ]
    fieldsets = (
        (
            "Значение Характеристики",
            {"fields": ("value_specification",)},
        ),
        (
            "Переводы на языки",
            {"fields": ("additional_data",)},
        ),
    )
