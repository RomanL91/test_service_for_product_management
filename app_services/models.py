from django.db import models

from core.mixins import JSONFieldsMixin

from app_sales_points.models import City


class Service(JSONFieldsMixin, models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cities = models.ManyToManyField(City, related_name="services")

    class Meta:
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"

    def __str__(self):
        return self.name
