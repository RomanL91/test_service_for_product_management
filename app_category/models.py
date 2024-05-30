from django.db import models

from mptt.models import MPTTModel, TreeForeignKey


class JSONFieldsMixin(models.Model):
    def default_additional_data():
        d = {"RU": "", "EN": "", "KZ": ""}
        return d

    additional_data = models.JSONField(
        verbose_name="Дополнительные данные",
        blank=True,
        null=True,
        default=default_additional_data(),
    )

    class Meta:
        abstract = True


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


class Brand(models.Model):
    name_brand = models.CharField(max_length=100, verbose_name="Название бренда")

    class Meta:
        verbose_name = "Брэнд"
        verbose_name_plural = "Брэнды"

    def __str__(self):
        return self.name_brand
