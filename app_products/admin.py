from django.contrib import admin

from app_products.models import Products


admin.site.site_header = "Администрирование Магазина"
admin.site.index_title = "Администрирование Магазина"  # default: "Site administration"
admin.site.site_title = "Администрирование Магазина"  # default: "Django site admin"
admin.site.site_url = None
# admin.site.disable_action('delete_selected')

admin.site.register(Products)
