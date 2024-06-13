from django.db import models
from django.contrib import admin

from flat_json_widget.widgets import FlatJsonWidget

from core.mixins import JsonDocumentForm
from app_specifications.models import Specifications


class SpecificationsInline(admin.StackedInline):
    model = Specifications
    max_num = 100
    extra = 0
    formfield_overrides = {models.JSONField: {"widget": FlatJsonWidget}}


@admin.register(Specifications)
class SpecificationAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
    list_display = [
        "name_specification",
    ]
    search_fields = [
        "name_specification",
    ]
