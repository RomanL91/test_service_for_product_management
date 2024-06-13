from django.db import models

from core.mixins import JSONFieldsMixin
from app_products.models import Products


class Specifications(JSONFieldsMixin, models.Model):
    name_specification = models.CharField(
        max_length=150,
        verbose_name="Название характеристики",
    )
    value_specification = models.CharField(
        max_length=150,
        verbose_name="Значение характеристики",
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Продукт",
    )

    # measurement_system = models.ForeignKey(MeasurementSystem)

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
        # TODO ограничение уникальности сочетания
        # имени характеристики и продукта

    def __str__(self) -> str:
        return self.name_specification


# TODO
# class MeasurementSystem(models.Model): # система измерений
#     pass
