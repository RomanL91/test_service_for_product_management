from django.db import models

from app_brands.models import Brands
from app_category.models import Category


class ExtProduct(models.Model):
    product_name = models.CharField(
        max_length=255,
        verbose_name="Наименование товара",
        blank=True,
    )
    vendor_code = models.CharField(
        max_length=30,
        verbose_name="Артикул продукта",
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        null=True,
        default=None,
    )

    # Добавим обязательные поля из модели Products
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        verbose_name="Категория продукта",
        related_name="ext_products",
    )
    brand = models.ForeignKey(
        Brands,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        verbose_name="Бренд продукта",
        related_name="ext_products",
    )

    class Meta:
        verbose_name = "Внешний Продукт"
        verbose_name_plural = "Внешние Продукты"

    def __str__(self):
        return f"{self.product_name} ({self.vendor_code})"


class ExtProductImage(models.Model):
    image = models.ImageField(
        verbose_name="Изображение",
        blank=True,
        upload_to="product_images/%Y/%m/%d/%H/%M/%S/",
    )
    product = models.ForeignKey(
        ExtProduct,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self) -> str:
        return self.product.product_name


class City(models.Model):
    name_city = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название города",
    )
    # Другие поля, если необходимо

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.name_city


class Warehouse(models.Model):
    external_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Внешний ID",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        related_name="warehouses",
        verbose_name="Выбор города",
    )
    name_warehouse = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название склада",
    )
    # Другие поля, если необходимо

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self):
        # return f"{self.name_warehouse} ({self.city.name_city})"
        return f"{self.name_warehouse}"


class Stock(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        related_name="stocks",
        verbose_name="Выбор склада",
    )
    product = models.ForeignKey(
        ExtProduct,
        on_delete=models.CASCADE,
        related_name="stocks",
        verbose_name="Выбор продукта",
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Колличество",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
    )
    # Другие поля, если необходимо

    class Meta:
        verbose_name = "Остаток/Цена"
        verbose_name_plural = "Остатки/Цены"

    def __str__(self):
        # return f"{self.product.name_product} в {self.warehouse.name_warehouse} ({self.quantity} шт. по {self.price})"
        return f"{self.product.product_name} ({self.quantity} шт. по {self.price})"


class Specifications(models.Model):
    name_specification = models.ForeignKey(
        "NameSpecifications",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Название характеристики",
        help_text="Выберите название для характеристики или создайте новое",
    )
    value_specification = models.ForeignKey(
        "ValueSpecifications",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Значение характеристики",
        help_text="Выберите значение для характеристики или создайте новое",
    )
    product = models.ForeignKey(
        ExtProduct,
        on_delete=models.SET_NULL,
        null=True,
        related_name="specifications",
        verbose_name="Продукт",
    )

    # measurement_system = models.ForeignKey(MeasurementSystem)

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
        # TODO ограничение уникальности сочетания
        # имени характеристики и продукта

    def __str__(self) -> str:
        return str(self.name_specification)


class NameSpecifications(models.Model):
    name_specification = models.CharField(
        max_length=150,
        verbose_name="Название характеристики",
    )

    class Meta:
        verbose_name = "Название характеристики"
        verbose_name_plural = "Название характеристик"

    def __str__(self) -> str:
        return self.name_specification


class ValueSpecifications(models.Model):
    value_specification = models.CharField(
        max_length=150,
        verbose_name="Значение характеристики",
    )

    class Meta:
        verbose_name = "Значение характеристики"
        verbose_name_plural = "Значение характеристик"

    def __str__(self) -> str:
        return self.value_specification
