from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.contenttypes.fields import GenericRelation

from core.mixins import JSONFieldsMixin
from core.TranslationDecorator import register_for_translation


@register_for_translation("name_brand", "additional_data")
class Brands(JSONFieldsMixin, models.Model):
    name_brand = models.CharField(
        max_length=150,
        verbose_name="Наименование бренда",
    )
    edges = GenericRelation(
        "app_sales_points.Edges",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    class Meta:
        indexes = [
            models.Index(fields=["name_brand"]),
            GinIndex(
                fields=["name_brand"],
                name="trgm_idx_name_brand",
                opclasses=["gin_trgm_ops"],
            ),
        ]
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def get_name(self):
        return self.name_brand

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
