from django.db import models

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def valid(value):
    if value < 0:
        raise ValidationError(
            _("%(value)s Не может быть отрицательным"),
            params={"value": value},
        )


class Products(models.Model):
    # ================= Категории
    # category = models.ForeignKey(
    #     Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория продукта'
    # )
    # ================= Имя, Описание
    name_product = models.CharField(
        verbose_name="Наименование продукта", max_length=150
    )
    desc_product = models.TextField(
        verbose_name="Описание продукта", max_length=1000, blank=True
    )
    # ================= Все связанное с ценой продукта
    price = models.DecimalField(
        verbose_name="Цена",
        validators=[
            valid,
        ],
        max_digits=15,
        decimal_places=2,
        default=0,
        blank=True,
        null=True,
    )
    # ================= Остаток продукта
    remaining_goods = models.PositiveIntegerField(
        verbose_name="Остаток товара", default=0, blank=True
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self) -> str:
        return self.name_product


# class ProductImage(models.Model):
#     image = models.ImageField(verbose_name='Изображение', blank=True, upload_to='product_images/%Y/%m/%d/%H/%M/%S/')
#     desc = models.TextField(verbose_name='Описание', max_length=1500, blank=True)
#     product = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='Продукт')

#     class Meta:
#             verbose_name = 'Изображение'
#             verbose_name_plural = 'Изображения'


#     def __str__(self) -> str:
#         return self.product.name_product