from django.db import models
from django.contrib import admin

from django.utils.html import mark_safe

from core.mixins import JsonDocumentForm, CustomAdminFileWidget

from app_blogs.models import Blog, BlogImage


class BlogImageInline(admin.StackedInline):
    model = BlogImage
    max_num = 3
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    filter_horizontal = [
        "related_product",
    ]
    inlines = [
        BlogImageInline,
    ]


@admin.register(BlogImage)
class BlogtImageAdmin(admin.ModelAdmin):
    readonly_fields = ["preview"]
    list_display = [
        "get_image",
        "blog",
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
