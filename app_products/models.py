from django.db import models

from core.mixins import JSONFieldsMixin

from app_category.models import Category


class Products(JSONFieldsMixin, models.Model):
    name_product = models.CharField(
        max_length=150,
        verbose_name="Наименование продукта",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория продукта",
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self) -> str:
        return self.name_product


class ProductImage(models.Model):
    image = models.ImageField(
        verbose_name="Изображение",
        blank=True,
        upload_to="product_images/%Y/%m/%d/%H/%M/%S/",
    )
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, verbose_name="Продукт"
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self) -> str:
        return self.product.name_product
