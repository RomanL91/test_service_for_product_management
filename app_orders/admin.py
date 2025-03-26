from collections import Counter

from django.contrib import admin
from django.utils.html import format_html

from django.contrib.auth.models import User
from app_orders.models import Baskets, Orders
from app_products.models import Products


@admin.register(Baskets)
class BasketsAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"

    list_display = [
        "id",
        "uuid_id",
        "user_id",
        "completed",
        "checkout_stage",
        "created_at",
        "updated_at",
    ]

    list_filter = [
        "completed",
        "checkout_stage",
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
    )
    exclude = [
        "gift_items",
        "basket_items",
    ]

    class Media:
        js = ("admin/custom.js",)

    def products_summary_with_actions(self, obj):
        if not obj.basket_items:
            return "No products"

        prod_with_count = dict(Counter(obj.basket_items))

        products = Products.objects.filter(id__in=obj.basket_items)

        # Формируем строку с продуктами
        products_html = "<br><br>".join(
            [
                f"""
                {(
                    f'<img src="{prod.productimage_set.first().image.url}" style="max-height: 100px; max-width: 100px;">'
                    if prod.productimage_set.first() else "Изображение отсутствует"
                )}
                <a href='{prod.get_admin_url()}'>{ind+1:0.0f}) {prod.name_product}</a>
                <ul>в количестве: {prod_with_count.get(prod.pk, None)} у.е.</ul>
                <br>
                    {
                        "".join([f"<li>Склад: {stock.warehouse} цена = {stock.price} | суммарно за позицию (цена*у.е.) = {stock.price*prod_with_count.get(prod.pk, None)}</li>" for stock in prod.stocks.all()])
                    }
                <br>
                <hr>
                """
                for ind, prod in enumerate(products)
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

    products_summary_with_actions.short_description = "Обзор товаров в корзине"


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = [
        "user_full_name",
        "phone_number",
        "shipping_city",
        "delivery_type",
        "total_amount",
        "payment_type",
        "order_status",
        "payment_status",
    ]
    list_filter = [
        "shipping_city",
        "delivery_type",
        "payment_type",
        "order_status",
        "payment_status",
        "manager_executive",
    ]
    search_fields = [
        "user_full_name",
        "total_amount",
        "comment",
        "delivery_address",
        "account_number",
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manager_executive":
            kwargs["initial"] = request.user  # Подставляем текущего пользователя

            if request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(
                    is_staff=True
                )  # Все администраторы
            else:
                kwargs["queryset"] = User.objects.filter(
                    pk=request.user.id, is_staff=True
                )  # Только текущий пользователь

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# @admin.register(Transactionpayments)
# class TransactionpaymentsAdmin(admin.ModelAdmin):
#     pass
