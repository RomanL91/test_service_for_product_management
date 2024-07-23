from django.contrib import admin

from app_kaspi.models import Token, Order, Customer, Address, Product, KaspiDelivery


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    pass


admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Product)
admin.site.register(KaspiDelivery)
