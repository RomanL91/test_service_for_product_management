from django.db import models

from core.mixins import JSONFieldsMixin
from app_products.models import Products


class Specifications(models.Model):
    name_specification = models.ForeignKey(
        'NameSpecifications',
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
    
class NameSpecifications(JSONFieldsMixin, models.Model):
    name_specification = models.CharField(
        max_length=150,
        verbose_name="Название характеристики",
    )

    class Meta:
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
        verbose_name = "Значение характеристики"
        verbose_name_plural = "Значение характеристик"

    def __str__(self) -> str:
        return self.value_specification


# TODO
# class MeasurementSystem(models.Model): # система измерений
#     pass
