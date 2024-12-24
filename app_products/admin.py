from django.db import models
from django.contrib import admin

from django.utils.html import mark_safe

from core.mixins import JsonDocumentForm, CustomAdminFileWidget
from app_products.models import (
    Products,
    ProductImage,
    PopulatesProducts,
    ExternalProduct,
    ExternalProductImage,
)
from app_specifications.admin import SpecificationsInline
from app_sales_points.admin import StockInline

# форма для вывода древовидной структуры категорий
# from app_products.forms import ProductAdminForm


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    max_num = 10
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}
    # classes = ["collapse"] # свернуть (show/hide)


class ExternalProductImageInline(admin.StackedInline):
    model = ExternalProductImage
    max_num = 10
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}


class ProductAdmin(admin.ModelAdmin):
    # form = ProductAdminForm   # форма для вывода древовидной структуры категорий
    form = JsonDocumentForm
    inlines = [
        ProductImageInline,
        SpecificationsInline,
        StockInline,
    ]
    list_display = [
        "name_product",
        "category",
        # "price",
        # "remaining_goods",
        "get_image",
    ]
    list_filter = [
        "category",
        "brand",
    ]
    autocomplete_fields = [
        "category",
        "brand",
        "description",
    ]
    search_fields = [
        "name_product__istartswith",
        "name_product__iexact",
        "name_product__icontains",
        "vendor_code__iexact",
    ]
    readonly_fields = [
        "get_preview",
    ]
    filter_horizontal = [
        "related_product",
        "tag_prod",
        "present",
        "services",
        "configuration",
    ]
    prepopulated_fields = {"slug": ("name_product",)}
    fieldsets = (
        (
            "О продукте",
            {"fields": ("vendor_code", "name_product", "slug")},
        ),
        (
            "Переводы на языки",
            # {"fields": (("additional_data",),), "classes": ("collapse",)},
            {"fields": ("additional_data",)},
        ),
        (
            "Категория",
            {"fields": ("category",)},
        ),
        (
            "Бренд",
            {"fields": ("brand",)},
        ),
        (
            "Описание",
            {"fields": ("description",), "classes": ("collapse",)},
        ),
        (
            "Комплектации",
            {"fields": ("configuration",), "classes": ("collapse",)},
        ),
        (
            "Сопутсвующий товар",
            {"fields": ("related_product",), "classes": ("collapse",)},
        ),
        # (
        #     "Теги продукта",
        #     {"fields": ("tag_prod",)},
        # ),
        # (
        #     "В подарок",
        #     {"fields": ("present",)},
        # ),
        # (
        #     "Услуги к продукту",
        #     {"fields": ("services",)},
        # ),
    )

    def get_image(self, obj):
        return self.get_image_or_preview(obj, preview=False)

    get_image.short_description = "ФОТО"

    def get_preview(self, obj):
        return self.get_image_or_preview(obj, preview=True)

    get_preview.short_description = "ФОТО"

    def get_image_or_preview(self, obj, preview=False):
        try:
            url_prod = obj.productimage_set.all()[0].image.url
            width = 75 if not preview else 300
            return mark_safe(f'<img src={url_prod} width="{width}"')
        except:
            return None


class ProductImageAdmin(admin.ModelAdmin):
    readonly_fields = ["preview"]
    list_display = [
        "get_image",
        "product",
    ]

    def preview(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="600" ')

    preview.short_description = "Предпоказ"

    def get_image(self, obj):
        try:
            url_prod = obj.image.url
            return mark_safe(f'<img src={url_prod} width="75"')
        except:
            return None

    get_image.short_description = "ФОТО"


class PopulatesProductsAdmin(admin.ModelAdmin):
    list_display = [
        "name_set",
        "activ_set",
    ]
    filter_horizontal = [
        "products",
    ]


class ExternalProductAdmin(admin.ModelAdmin):
    inlines = [
        ExternalProductImageInline,
    ]
    search_fields = [
        "product_name__istartswith",
        "product_name__iexact",
        "product_name__icontains",
        "product_code__iexact",
    ]
    list_display = [
        "product_name",
        "product_code",
        "price",
        "stock",
        "category",
        "brand",
    ]
    list_filter = [
        "stock",
        "warehouse_code",
    ]
    list_editable = [
        "category",
        "brand",
    ]
    autocomplete_fields = ("category", "brand")
    list_per_page = 20


admin.site.register(PopulatesProducts, PopulatesProductsAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Products, ProductAdmin)
admin.site.register(ExternalProduct, ExternalProductAdmin)
