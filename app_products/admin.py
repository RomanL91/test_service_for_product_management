from django.contrib import admin
from django.db import models

from django.utils.html import mark_safe
from django.utils.html import format_html
from django.contrib.admin.widgets import AdminFileWidget

from app_products.models import Products, ProductImage
from app_products.forms import ProductAdminForm


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


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    max_num = 10
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}
    classes = ["collapse"]


# @admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [
        ProductImageInline,
    ]
    list_display = [
        "name_product",
        "category",
        "price",
        "remaining_goods",
        "get_image",
    ]

    def get_image(self, obj):
        try:
            url_prod = obj.productimage_set.all()[0].image.url
            return mark_safe(f'<img src={url_prod} width="75"')
        except:
            return None
    get_image.short_description = 'ФОТО'


# @admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    readonly_fields = ["preview"]
    list_display = ["get_image", "product", "desc"]

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


admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Products, ProductAdmin)


admin.site.site_header = "Администрирование Магазина"
admin.site.index_title = "Администрирование Магазина"  # default: "Site administration"
admin.site.site_title = "Администрирование Магазина"  # default: "Django site admin"
admin.site.site_url = None
# admin.site.disable_action('delete_selected')
