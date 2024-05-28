from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin

from app_category.models import Category


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    list_display = [
        "name_category",
        "desc_category",
    ]
