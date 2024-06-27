from django import forms
from django.contrib import admin

from core.mixins import JsonDocumentForm

from app_manager_tags.models import Tag, ColorField


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    formfield_overrides = {
        ColorField: {"widget": forms.TextInput(attrs={"type": "color"})}
    }
