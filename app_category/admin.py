from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin

from core.mixins import JsonDocumentForm
from app_category.models import Category


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    form = JsonDocumentForm
    list_display = [
        "name_category",
    ]
    search_fields = [
        "name_category",
    ]
