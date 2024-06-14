from django.db import models

from core.mixins import JSONFieldsMixin, JSONFieldsDescMixin
from app_products.models import Products


class BaseDescription(JSONFieldsMixin, models.Model):
    title_description = models.CharField(
        max_length=150, verbose_name="Заголовок описания"
    )

    class Meta:
        verbose_name = "Описание"
        verbose_name_plural = "Описания"

    def __str__(self) -> str:
        return self.title_description


class ProductDescription(BaseDescription, JSONFieldsDescMixin):
    body_description = models.TextField(
        verbose_name="Описание",
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )

    class Meta:
        verbose_name = "Описание для продукта"
        verbose_name_plural = "Описания для продуктов"

    def __str__(self) -> str:
        return self.title_description
