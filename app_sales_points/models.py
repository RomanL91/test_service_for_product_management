from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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


class Edges(models.Model):
    edges_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название направления",
        help_text="Укажите имя для маршрута/направления/ребра. Дожно быть уникальным",
    )
    city_from = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        related_name="edges_from",
        verbose_name="С города",
        help_text="Укажите начальную точку маршрута",
    )
    city_to = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        related_name="edges_to",
        verbose_name="В город",
        help_text="Укажите конечную точку маршрута",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(app_label="app_category", model="category")
        | models.Q(app_label="app_brands", model="brands"),
        verbose_name="Объект маршрута",
        help_text="Выбирите к чему нужно применить маршрут",
    )
    object_id = models.PositiveIntegerField(editable=False)
    obj = GenericForeignKey("content_type", "object_id")
    estimated_delivery_days = models.PositiveIntegerField(
        verbose_name="Срок доставки (в днях)",
        default=3,
        help_text="Количество дней для доставки по маршруту",
    )
    transportation_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Транспортировочные расходы",
        default=0.00,
        help_text="Возможная наценка на объект маршрута",
    )
    is_active = models.BooleanField(
        verbose_name="Активный статус",
        default=True,
        help_text="Определяет, является ли маршрут активным. Можно включить/выключить для использования",
    )
    expiration_date = models.DateField(
        verbose_name="Дата истечения срока действия",
        help_text="Дата, до которой (не включительно) маршрут используется системой",
    )

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["city_from", "city_to", "object_id"],
                name="unique_edge_constraint",  # Уникальное ограничение
            )
        ]

    def __str__(self):
        return f"{self.city_from} -> {self.city_to}"
