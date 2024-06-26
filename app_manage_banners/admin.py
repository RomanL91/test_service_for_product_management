from django.contrib import admin

from app_manage_banners.models import BannerImage


@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    pass
