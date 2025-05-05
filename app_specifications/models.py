from django.db import models
from django.contrib.postgres.indexes import GinIndex

from core.mixins import JSONFieldsMixin
from app_products.models import Products


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
        Products,
        on_delete=models.SET_NULL,
        null=True,
        related_name="specifications",
        verbose_name="Продукт",
    )
    ind = models.PositiveIntegerField(
        verbose_name="Порядковый номер",
        default=0,
    )

    # measurement_system = models.ForeignKey(MeasurementSystem)

    class Meta:
        ordering = ["ind"]
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
        indexes = [
            models.Index(fields=["name_specification"]),
            models.Index(fields=["value_specification"]),
            models.Index(fields=["product"]),
            models.Index(fields=["name_specification", "value_specification"]),
        ]
        # TODO ограничение уникальности сочетания
        # имени характеристики и продукта

    def __str__(self) -> str:
        return str(self.name_specification)


class NameSpecifications(JSONFieldsMixin, models.Model):
    name_specification = models.CharField(
        max_length=150,
        verbose_name="Название характеристики",
    )

    class Meta:
        indexes = [
            GinIndex(
                fields=["name_specification"],
                name="trgm_idx_name_spec",
                opclasses=["gin_trgm_ops"],
            ),
        ]
        verbose_name = "Название характеристики"
        verbose_name_plural = "Название характеристик"

    def __str__(self) -> str:
        return self.name_specification


class ValueSpecifications(JSONFieldsMixin, models.Model):
    value_specification = models.CharField(
        max_length=150,
        verbose_name="Значение характеристики",
    )

    class Meta:
        indexes = [
            GinIndex(
                fields=["value_specification"],
                name="trgm_idx_value_spec",
                opclasses=["gin_trgm_ops"],
            ),
        ]
        verbose_name = "Значение характеристики"
        verbose_name_plural = "Значение характеристик"

    def __str__(self) -> str:
        return self.value_specification


# TODO
# class MeasurementSystem(models.Model): # система измерений
#     pass
