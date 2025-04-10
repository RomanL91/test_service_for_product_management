import json

from time import sleep

from django.db import models
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse, path

from app_external_products.models import (
    ExtProduct,
    ExtProductImage,
    City,
    Warehouse,
    Stock,
    Specifications,
    NameSpecifications,
    ValueSpecifications,
)

from app_external_products.utils import (
    get_price,
    extract_features,
    get_medium_links,
    save_images_for_product,
    create_specifications_from_list,
    send_message_rmq,
    global_session_storage,
)

from core.mixins import CustomAdminFileWidget


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/134.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;"
        "q=0.8,application/signed-exchange;v=b3;q=0.7"
    ),
    "Referer": "https://kaspi.kz/mc/",
}


# 1. Инлайны
class StockInline(admin.TabularInline):
    model = Stock
    extra = 1
    autocomplete_fields = ("warehouse",)  # автокомплит для склада


class SpecificationsInline(admin.TabularInline):
    model = Specifications
    extra = 1
    autocomplete_fields = ("name_specification", "value_specification")


class ExternalProductImageInline(admin.StackedInline):
    model = ExtProductImage
    max_num = 10
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}


@admin.register(ExtProduct)
class ExtProductAdmin(admin.ModelAdmin):
    list_display = ("product_name", "vendor_code", "brand", "category")
    search_fields = ("product_name", "vendor_code")
    list_filter = ("brand", "category")

    # Автокомплит для полей brand и category
    autocomplete_fields = ("brand", "category")

    # Подключаем инлайны
    inlines = [StockInline, SpecificationsInline, ExternalProductImageInline]

    # 1) Переопределяем шаблон для change_form
    change_form_template = "admin/app_external_products/extprod/change_form.html"

    # 2) Переопределяем get_urls, чтобы добавить кастомный урл
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/<int:idpk>/do-spec/",
                self.admin_site.admin_view(self.load_spec),
                name="load_spec",
            ),
            path(
                "<int:object_id>/<int:idpk>/do-img/",
                self.admin_site.admin_view(self.load_img),
                name="load_img",
            ),
            path(
                "<int:object_id>/<int:idpk>/do-price/",
                self.admin_site.admin_view(self.load_price),
                name="load_price",
            ),
        ]
        return custom_urls + urls

    # 3) Наш метод, который будет вызываться при нажатии на кнопку
    def load_spec(self, request, object_id, idpk):
        data_msg = {"object_id": object_id, "idpk": idpk, "base_prod": False}
        msg = json.dumps(data_msg)
        send_message_rmq(message=msg)
        # try:
        #     session = global_session_storage.do_authorization()
        #     url = (
        #         f"https://mc.shop.kaspi.kz/bff/offer-view/details?m=BUGA&s={object_id}"
        #     )
        #     if session:
        #         r = session.get(
        #             url,
        #             headers=HEADERS,
        #         )
        #         res = r.json()
        #         master_product = res.get("masterProduct")
        #         spec = master_product.get("specifications")
        #         extract_spec = extract_features(spec)
        #         create_specifications_from_list(extract_spec, idpk)

        #         self.message_user(request, "Подкачка успешна!")
        #         # Возвращаем пользователя обратно на форму редактирования
        #         # Используем META['HTTP_REFERER'], чтобы вернуться, или просто:
        #         # return redirect("admin:appname_extproduct_change", object_id)
        #         return redirect(
        #             request.META.get("HTTP_REFERER") or reverse("admin:index")
        #         )
        #     self.message_user(request, "Сессия сдохла", level="error")

        # except Exception as e:
        #     self.message_user(request, str(e), level="error")
        #     return redirect(request.META.get("HTTP_REFERER") or reverse("admin:index"))
        sleep(5)
        self.message_user(request, "Подкачка успешна!")
        return redirect(request.META.get("HTTP_REFERER") or reverse("admin:index"))

    def load_img(self, request, object_id, idpk):
        try:
            session = global_session_storage.do_authorization()
            url = (
                f"https://mc.shop.kaspi.kz/bff/offer-view/details?m=BUGA&s={object_id}"
            )
            if session:
                r = session.get(
                    url,
                    headers=HEADERS,
                )
                res = r.json()
                master_product = res.get("masterProduct")
                gallery_images = master_product.get("galleryImages")
                medium_links_img = get_medium_links(gallery_images)
                save_images_for_product(medium_links_img, idpk)
                self.message_user(request, "Подкачка успешна!")
                return redirect(
                    request.META.get("HTTP_REFERER") or reverse("admin:index")
                )
            self.message_user(request, "Сессия сдохла", level="error")

        except Exception as e:
            self.message_user(request, str(e), level="error")
            return redirect(request.META.get("HTTP_REFERER") or reverse("admin:index"))

    def load_price(self, request, object_id, idpk):
        try:
            session = global_session_storage.do_authorization()
            url = (
                f"https://mc.shop.kaspi.kz/bff/offer-view/details?m=BUGA&s={object_id}"
            )
            if session:
                r = session.get(
                    url,
                    headers=HEADERS,
                )
                res = r.json()
                availabilities = res.get("availabilities", [])
                cityInfo = res.get("cityInfo", [])
                get_price(availabilities, cityInfo, idpk)
                self.message_user(request, "Подкачка успешна!")
                return redirect(
                    request.META.get("HTTP_REFERER") or reverse("admin:index")
                )

            self.message_user(request, "Сессия сдохла", level="error")
        except Exception as e:
            self.message_user(request, str(e), level="error")
            return redirect(request.META.get("HTTP_REFERER") or reverse("admin:index"))


@admin.register(NameSpecifications)
class NameSpecificationsAdmin(admin.ModelAdmin):
    list_display = ("name_specification",)
    search_fields = ("name_specification",)


@admin.register(ValueSpecifications)
class ValueSpecificationsAdmin(admin.ModelAdmin):
    list_display = ("value_specification",)
    search_fields = ("value_specification",)


# 4. Город, склад и остатки
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name_city",)
    search_fields = ("name_city",)


class StockInlineForWarehouse(admin.TabularInline):
    model = Stock
    extra = 1
    autocomplete_fields = ("product",)  # автокомплит по продукту


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name_warehouse", "city", "external_id")
    search_fields = ("name_warehouse", "external_id")

    # Автокомплит по городу, если нужно
    autocomplete_fields = ("city",)

    inlines = [StockInlineForWarehouse]


@admin.register(Specifications)
class SpecificationsAdmin(admin.ModelAdmin):
    list_display = ("product", "name_specification", "value_specification")
    list_filter = ("name_specification", "value_specification")
    search_fields = ("product__product_name",)

    # Можно добавить автокомплит и тут
    autocomplete_fields = ("product", "name_specification", "value_specification")
