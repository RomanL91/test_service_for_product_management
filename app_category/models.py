from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

from core.mixins import JSONFieldsMixin, SlugModelMixin


class Category(MPTTModel, JSONFieldsMixin, SlugModelMixin):
    name_category = models.CharField(
        max_length=100,
        verbose_name="Имя категории",
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


class CategoryImage(models.Model):
    image = models.ImageField(
        verbose_name="Изображение",
        blank=True,
        upload_to="product_images/%Y/%m/%d/%H/%M/%S/",
        help_text="Это миниатюрное представление изображения категории.",
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория"
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self) -> str:
        return self.category.name_category
