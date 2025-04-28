import json

from time import sleep

from django.db import models
from django.contrib import admin

from django.utils.html import mark_safe

from core.mixins import JsonDocumentForm, CustomAdminFileWidget
from app_products.models import (
    Products,
    ProductImage,
    PopulatesProducts,
    ExternalProduct,
    ExternalProductImage,
)
from app_specifications.admin import SpecificationsInline
from app_sales_points.admin import StockInline

from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from adminsortable2.admin import SortableAdminBase
from adminsortable2.admin import SortableStackedInline

from app_external_products.utils import send_message_rmq


class ProductImageInline(SortableStackedInline, admin.StackedInline):
    model = ProductImage
    max_num = 10
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}
    # classes = ["collapse"] # свернуть (show/hide)


class ExternalProductImageInline(admin.StackedInline):
    model = ExternalProductImage
    max_num = 10
    extra = 0
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}


from django.shortcuts import redirect
from django.urls import reverse, path
from app_products.utils import (
    get_price,
    extract_features,
    get_medium_links,
    save_images_for_product,
    create_specifications_from_list,
    global_session_storage,
)

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


class ProductAdmin(AutocompleteFilterMixin, SortableAdminBase, admin.ModelAdmin):
    change_form_template = "admin/app_products/prod/change_form.html"
    form = JsonDocumentForm
    inlines = [
        ProductImageInline,
        SpecificationsInline,
        StockInline,
    ]
    list_display = [
        "name_product",
        "category",
        # "price",
        # "remaining_goods",
        "get_image",
    ]
    list_filter = [
        # "category",
        ("category", AutocompleteListFilter),
        "brand",
    ]
    autocomplete_fields = [
        "category",
        "brand",
        "description",
    ]
    search_fields = [
        "name_product__istartswith",
        "name_product__iexact",
        "name_product__icontains",
        "vendor_code__iexact",
    ]
    readonly_fields = [
        "get_preview",
    ]
    filter_horizontal = [
        "related_product",
        "tag_prod",
        "present",
        "services",
        "configuration",
    ]
    prepopulated_fields = {"slug": ("name_product",)}
    fieldsets = (
        (
            "О продукте",
            {"fields": ("vendor_code", "name_product", "slug")},
        ),
        (
            "Переводы на языки",
            # {"fields": (("additional_data",),), "classes": ("collapse",)},
            {"fields": ("additional_data",)},
        ),
        (
            "Категория",
            {"fields": ("category",)},
        ),
        (
            "Бренд",
            {"fields": ("brand",)},
        ),
        (
            "Описание",
            {"fields": ("description",), "classes": ("collapse",)},
        ),
        (
            "Комплектации",
            {"fields": ("configuration",), "classes": ("collapse",)},
        ),
        (
            "Сопутсвующий товар",
            {"fields": ("related_product",), "classes": ("collapse",)},
        ),
        (
            "Теги продукта",
            {"fields": ("tag_prod",), "classes": ("collapse",)},
        ),
        # (
        #     "В подарок",
        #     {"fields": ("present",)},
        # ),
        (
            "Услуги к продукту",
            {"fields": ("services",), "classes": ("collapse",)},
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/<int:idpk>/do-spec/",
                self.admin_site.admin_view(self.load_spec),
                name="load_spec_base",
            ),
            path(
                "<int:object_id>/<int:idpk>/do-img/",
                self.admin_site.admin_view(self.load_img),
                name="load_img_base",
            ),
            path(
                "<int:object_id>/<int:idpk>/do-price/",
                self.admin_site.admin_view(self.load_price),
                name="load_price_base",
            ),
        ]
        return custom_urls + urls

    # 3) Наш метод, который будет вызываться при нажатии на кнопку
    def load_spec(self, request, object_id, idpk):
        data_msg = {"object_id": object_id, "idpk": idpk}
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

    def get_image(self, obj):
        return self.get_image_or_preview(obj, preview=False)

    get_image.short_description = "ФОТО"

    def get_preview(self, obj):
        return self.get_image_or_preview(obj, preview=True)

    get_preview.short_description = "ФОТО"

    def get_image_or_preview(self, obj, preview=False):
        try:
            url_prod = obj.productimage_set.all()[0].image.url
            width = 75 if not preview else 300
            return mark_safe(f'<img src={url_prod} width="{width}"')
        except:
            return None


class ProductImageAdmin(admin.ModelAdmin):
    readonly_fields = ["preview"]
    list_display = [
        "get_image",
        "product",
    ]

    def preview(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="600" ')

    preview.short_description = "Предпоказ"

    def get_image(self, obj):
        try:
            url_prod = obj.image.url
            return mark_safe(f'<img src={url_prod} width="75"')
        except:
            return None

    get_image.short_description = "ФОТО"


class PopulatesProductsAdmin(admin.ModelAdmin):
    list_display = [
        "name_set",
        "activ_set",
    ]
    filter_horizontal = [
        "products",
    ]


class ExternalProductAdmin(admin.ModelAdmin):
    inlines = [
        ExternalProductImageInline,
    ]
    search_fields = [
        "product_name__istartswith",
        "product_name__iexact",
        "product_name__icontains",
        "product_code__iexact",
    ]
    list_display = [
        "product_name",
        "product_code",
        "price",
        "stock",
        "category",
        "brand",
    ]
    list_filter = [
        "stock",
        "warehouse_code",
    ]
    list_editable = [
        "category",
        "brand",
    ]
    autocomplete_fields = ("category", "brand")
    list_per_page = 20


admin.site.register(PopulatesProducts, PopulatesProductsAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Products, ProductAdmin)
admin.site.register(ExternalProduct, ExternalProductAdmin)
