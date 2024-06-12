from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

from core.mixins import JSONFieldsMixin


class Category(MPTTModel, JSONFieldsMixin):
    name_category = models.CharField(
        max_length=100,
        verbose_name="Имя категории",
    )
    desc_category = models.TextField(
        verbose_name="Описание категории", max_length=1000, blank=True
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        verbose_name="Родительская категория",
    )

    class MPTTMeta:
        order_insertion_by = ["name_category"]

    class Meta:
        unique_together = [["parent", "name_category"]]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name_category
