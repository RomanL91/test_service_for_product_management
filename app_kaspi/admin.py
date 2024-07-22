from django.contrib import admin

from app_kaspi.models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    pass
