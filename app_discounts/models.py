from django.db import models
from django.utils import timezone

from core.mixins import JSONFieldsMixin
from app_category.models import Category
from app_products.models import Products


class BaseDiscount(JSONFieldsMixin, models.Model):
    # Основные атрибуты скидки
    name = models.CharField(
        max_length=255,
        verbose_name="Название скидки",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание скидки",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Размер скидки",
    )

    # Управление действием скидки
    active = models.BooleanField(
        default=True,
        verbose_name="Активность скидки",
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата начала действия",
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата окончания действия",
    )

    def is_valid(self):
        """Проверяет, активна ли скидка и в допустимом ли диапазоне даты"""
        if not self.active:
            return False
        now = timezone.now()
        if self.start_date and self.start_date > now:
            self.active = False
            self.save()
            return False
        if self.end_date and self.end_date < now:
            self.active = False
            self.save()
            return False
        return True

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class ProductDiscount(BaseDiscount):
    products = models.ManyToManyField(
        Products,
        blank=True,
        verbose_name="Продукты",
    )

    class Meta:
        verbose_name = "Скидка на продук"
        verbose_name_plural = "Скидка на продукы"


class CategoryDiscount(BaseDiscount):
    categories = models.ManyToManyField(
        Category,
        blank=True,
        verbose_name="Категории",
    )

    class Meta:
        verbose_name = "Скидка на категорию"
        verbose_name_plural = "Скидка на категории"
