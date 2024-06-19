from django.db import models
from django.contrib import admin

from flat_json_widget.widgets import FlatJsonWidget

from core.mixins import JsonDocumentForm

from app_sales_points.models import City, Warehouse, Stock


class StockInline(admin.StackedInline):
    model = Stock
    max_num = 100
    extra = 0
    autocomplete_fields = ["warehouse"]
    formfield_overrides = {models.JSONField: {"widget": FlatJsonWidget}}


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = JsonDocumentForm


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    search_fields = [
        "name_warehouse",
    ]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    list_display = [
        "product",
    ]
    # search_fields = [
    #     "name_specification",
    # ]
    autocomplete_fields = [
        "product",
        "warehouse",
    ]
