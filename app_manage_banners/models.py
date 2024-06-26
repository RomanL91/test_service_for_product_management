from django.db import models
from django.core.exceptions import ValidationError

from app_category.models import Category


class BannerImage(models.Model):
    name_banner = models.CharField(
        max_length=150,
        verbose_name="Название банера",
    )
    image = models.ImageField(
        verbose_name="Изображение банера",
        blank=True,
        upload_to="product_images/%Y/%m/%d/%H/%M/%S/",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Банер"
        verbose_name_plural = "Баннеры"

    def __str__(self) -> str:
        return self.name_banner

    def clean(self):
        if self.category.level != 0:
            raise ValidationError(
                {
                    "category": "Баннер может быть создан только для категорий с уровнем 0."
                }
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
