from django.contrib import admin

from app_kaspi.models import Token, Order, Customer, Product


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "state",
        "status",
        "customer_kaspi",
        "product_in_orders",
    ]


admin.site.register(Customer)
admin.site.register(Product)
