from django.db import models

from core.mixins import JSONFieldsMixin


class Brands(JSONFieldsMixin, models.Model):
    name_brand = models.CharField(
        max_length=150,
        verbose_name="Наименование бренда",
    )

    class Meta:
        verbose_name = "бренд"
        verbose_name_plural = "бренды"

    def __str__(self) -> str:
        return self.name_brand


class LogoBrand(models.Model):
    image = models.ImageField(
        verbose_name="Логотип",
        blank=True,
        upload_to="logo_images/%Y/%m/%d/%H/%M/%S/",
    )
    brand = models.ForeignKey(
        Brands,
        on_delete=models.CASCADE,
        verbose_name="Бренд",
    )

    class Meta:
        verbose_name = "Логотип"
        verbose_name_plural = "Логотипы"

    def __str__(self) -> str:
        return self.brand.name_brand
