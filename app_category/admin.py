from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin

from app_category.models import Category, Brand


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    list_display = [
        "name_category",
        "desc_category",
    ]
    search_fields = [
        "name_category",
    ]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass
