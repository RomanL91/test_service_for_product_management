from django.contrib import admin

from core.mixins import JsonDocumentForm

from app_services.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = JsonDocumentForm
