from django.db import models
from django.contrib import admin
# from django.utils.html import mark_safe
# from django.utils.html import format_html
# from django.contrib.admin.widgets import AdminFileWidget

from app_products.models import Products

from decimal import Decimal

# from django_celery_beat.admin import (
#     PeriodicTask, SolarSchedule, 
#     ClockedSchedule, CrontabSchedule,
#     IntervalSchedule, 
# )


# class CustomAdminFileWidget(AdminFileWidget):
#     def render(self, name, value, attrs=None, renderer=None):
#         result = []
#         if hasattr(value, "url"):
#             result.append(
#                 f'''<a href="{value.url}" target="_blank">
#                       <img 
#                         src="{value.url}" alt="{value}" 
#                         width="100" height="100"
#                         style="object-fit: cover;"
#                       />
#                     </a>'''
#             )
#         result.append(super().render(name, value, attrs, renderer))
#         return format_html("".join(result))


# class ProductImageAdmin(admin.ModelAdmin):
#     readonly_fields = ["preview"]
#     list_display = [
#         'get_image',
#         'product',
#         'desc'
#     ]

#     def preview(self, obj):
#         return mark_safe(f'<img src={obj.image.url} width="600" ')
#     preview.short_description = 'Предпоказ'

    
#     def get_image(self, obj):
#         try:
#             url_prod = obj.image.url
#             return mark_safe(f'<img src={url_prod} width="75"')
#         except:
#             return None
#     get_image.short_description = 'ФОТО'


# class ProductImageInline(admin.StackedInline):
#     model = ProductImage
#     max_num = 10
#     extra = 0
#     formfield_overrides = {
#         models.ImageField: {'widget': CustomAdminFileWidget}
#     }
#     classes = ['collapse']


# class ProductAdmin(admin.ModelAdmin):
#     fieldsets = (
#         ('О продукте', {'fields': (('name_product', 'color', 'desc_product'),)}),
#         ('Остаток продукта', {'fields': (('remaining_goods', 'display_remaining_goods'),), 'classes':('collapse',)}),
#         ('Категория', {'fields': (('category',),), 'classes':('collapse',)}),
#         ('ТЭГИ', {'fields': (('tag', 'display_tag'),), 'classes':('collapse',)}),
#         ('Цена', {'fields': (('price',),('price_with_discount_or_PROMO', 'display_price')), 'classes':('collapse',)}),
#         ('Акция', {'fields': (('discount', 'display_discount'), 'discount_period'), 'classes':('collapse',)}),
#         ('ПРОМО', {'fields': (('promo', 'display_promo'),), 'classes':('collapse',)}),
#         ('Рейтинг', {'fields': (('display_reviews', 'rating'),), 'classes':('collapse',)}),
#     )
#     filter_horizontal = ['tag',]
#     inlines = [ProductImageInline,]
#     list_display = [
#         'get_image',
#         'name_product',
#         'category',
#         'display_price',
#         'price',
#         'price_with_discount_or_PROMO',
#         'display_discount',
#         'discount',
#         'display_promo',
#         'promo',
#         'display_remaining_goods',
#         'remaining_goods',
#         'display_reviews',
#         'rating'
#     ]
#     readonly_fields = ['price_with_discount_or_PROMO',]


#     def get_image(self, obj):
#         try:
#             url_prod = obj.productimage_set.all()[0].image.url
#             return mark_safe(f'<img src={url_prod} width="75"')
#         except:
#             return None
#     get_image.short_description = 'ФОТО'


#     def save_model(self, request, obj, form, change):
#         if not 'display_discount' in form.data and not 'display_promo' in form.data:
#             obj.price_with_discount_or_PROMO = Decimal(form.data.get('price'))
#         else:
#             try:            
#                 price = Decimal(form.data.get('price'))
#                 discount = Decimal(form.data.get('discount')) / 100
#                 discount_promo = obj.promo.discont_promo / 100
#             except AttributeError:
#                 discount_promo = 0

#             if 'display_discount' in form.data and 'display_promo' in form.data:
#                 price = price - (price * (discount + discount_promo))
#             elif 'display_discount' in form.data:
#                 price = price - (price * discount)
#             elif 'display_promo' in form.data:
#                 price = price - (price * discount_promo)

#             obj.price_with_discount_or_PROMO = price
#         obj.save()


admin.site.site_header = 'Администрирование Магазина'
admin.site.index_title = 'Администрирование Магазина'   # default: "Site administration"
admin.site.site_title = 'Администрирование Магазина'    # default: "Django site admin"
admin.site.site_url = None   
# admin.site.disable_action('delete_selected')

# admin.site.register(ProductImage, ProductImageAdmin)
# admin.site.register(Products, ProductAdmin)
admin.site.register(Products)

