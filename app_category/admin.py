from django import forms
from django.contrib import admin

from django_mptt_admin.admin import DjangoMpttAdmin
from flat_json_widget.widgets import FlatJsonWidget

from app_category.models import Category, Brand


class JsonDocumentForm(forms.ModelForm):
    class Meta:
        widgets = {"additional_data": FlatJsonWidget}


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    form = JsonDocumentForm
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
