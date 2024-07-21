from django.db import models

from core.mixins import JSONFieldsMixin

from app_products.models import Products


class City(JSONFieldsMixin, models.Model):
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


class Warehouse(JSONFieldsMixin, models.Model):
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
        return f"{self.name_warehouse} ({self.city.name_city})"


class Stock(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        related_name="stocks",
        verbose_name="Выбор склада",
    )
    product = models.ForeignKey(
        Products,
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
        return f"{self.product.name_product} ({self.quantity} шт. по {self.price})"
