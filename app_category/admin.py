from django.contrib import admin

from app_category.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name_category",
        "desc_category",
    ]
