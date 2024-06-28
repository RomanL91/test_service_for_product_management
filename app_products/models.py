from django.db import models

from core.mixins import JSONFieldsMixin, SlugModelMixin

from app_brands.models import Brands
from app_category.models import Category
from app_manager_tags.models import Tag


class Products(JSONFieldsMixin, SlugModelMixin, models.Model):
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
    brand = models.ForeignKey(
        Brands,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="бренд продукта",
    )

    related_product = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="Сопутствующий товар",
    )
    tag_prod = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name="Теги продукта",
    )
    present = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="В подарок",
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
        Products,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self) -> str:
        return self.product.name_product


class PopulatesProducts(models.Model):
    name_set = models.CharField(
        max_length=150,
        verbose_name="Название сета",
    )
    activ_set = models.BooleanField(
        verbose_name="Активность набора",
        default=False,
    )
    products = models.ManyToManyField(
        Products,
        blank=True,
        verbose_name="Список популярных продуктов",
    )

    class Meta:
        verbose_name = "Популярный продукт"
        verbose_name_plural = "Популярные продукты"

    def __str__(self) -> str:
        return self.name_set
