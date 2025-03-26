from uuid import uuid4

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from app_products.models import Products


def valid(value):
    if not 5 >= value >= 0:
        raise ValidationError(
            _("%(value)s Оценка может быть от 0 до 5"),
            params={
                "value": value,
            },
        )


class Review(models.Model):

    rating = models.PositiveIntegerField(
        verbose_name="Оценка/Рейтинг",
        default=5,
        validators=[
            valid,
        ],
    )
    review = models.TextField(
        verbose_name="Отзыв",
        max_length=2000,
        unique=True,
    )
    moderation = models.BooleanField(
        verbose_name="Модерация",
        default=False,
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        verbose_name="Продукт",
        related_name="reviews",
    )
    user_uuid = models.UUIDField(
        verbose_name="ID пользователя",
        blank=True,
        null=True,
        default=uuid4,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        verbose_name = "Отзыв/Рейтинг"
        verbose_name_plural = "Отзывы/Рейтинги"

    def __str__(self) -> str:
        return self.product.name_product
