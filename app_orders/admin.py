from django.contrib import admin
from django.utils.html import format_html

from django.conf import settings

from app_orders.models import Baskets, Orders


@admin.register(Baskets)
class BasketsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "uuid_id",
        "user_id",
        "completed",
        "checkout_stage",
        "created_at",
        "updated_at",
    ]

    readonly_fields = (
        "id",
        "uuid_id",
        "user_id",
        "created_at",
        "updated_at",
        "completed",
        "checkout_stage",
        "products_summary_with_actions",
        "gift_items",
        "basket_items",
    )

    class Media:
        js = ("admin/custom.js",)

    def products_summary_with_actions(self, obj):
        if not obj.basket_items:
            return "No products"

        # Формируем строку с продуктами
        products_html = "<br><br>".join(
            [
                f"""
                <img src="{product['prod']['list_url_to_image'][0]}" alt="{product['name']}" style="max-height: 100px; max-width: 100px;">
                <a class='button add-btn' data-product-url="{settings.API_URL_BASKET_ITEM_UPDATE.format(uuid_id=obj.uuid_id, prod_id=product['prod_id'])}" data-product-count="{product['count']}" href="#">[+]</a>
                <a class='button remove-btn' data-product-url="{settings.API_URL_BASKET_ITEM_UPDATE.format(uuid_id=obj.uuid_id, prod_id=product['prod_id'])}" data-product-count="{product['count']}" href="#">[-]</a>
                <a class='button delete-btn' data-product-url="{settings.API_URL_BASKET_ITEM_UPDATE.format(uuid_id=obj.uuid_id, prod_id=product['prod_id'])}" data-product-count="{product['count']}" href="#">[DEL]</a>
                <a href='{product["url"]}'>{ind+1:0.0f}) {product['name']}</a>
                <br>
                <ul>в количестве: {product['count']} у.е.</ul>
                <br>
                {
                    "".join([f"<li>в городе: {c} цена = {p} | суммарно за позицию (цена*у.е.) = {p*product['count']}</li>" for c, p in product['prod']['price'].items()])
                }
                <br>
                <hr>
                """
                for ind, product in enumerate(obj.basket_items)
            ]
        )

        # Добавляем кнопки управления
        # edit_url = reverse("admin:app_orders_baskets_change", args=[obj.id])
        # delete_url = reverse("admin:app_orders_baskets_delete", args=[obj.id])
        # buttons_html = f"""
        # <a class="button" href="{edit_url}">Edit</a>
        # <a class="button" href="{delete_url}" style="color:red;">Delete</a>
        # """
        # return format_html(f"{products_html}<br><br>{buttons_html}")
        return format_html(f"{products_html}")

    products_summary_with_actions.short_description = "Products Summary with Actions"


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    pass


# @admin.register(Transactionpayments)
# class TransactionpaymentsAdmin(admin.ModelAdmin):
#     pass
