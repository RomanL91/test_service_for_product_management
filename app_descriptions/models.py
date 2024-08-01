from django.db import models

from core.mixins import JSONFieldsMixin, JSONFieldsDescMixin


class BaseDescription(JSONFieldsMixin, models.Model):
    title_description = models.CharField(
        max_length=150, verbose_name="Заголовок описания"
    )

    class Meta:
        verbose_name = "Описание"
        verbose_name_plural = "Описания"

    def __str__(self) -> str:
        return self.title_description


class ProductDescription(BaseDescription, JSONFieldsDescMixin):
    body_description = models.TextField(
        verbose_name="Описание",
    )

    class Meta:
        verbose_name = "Описание для продукта"
        verbose_name_plural = "Описания для продуктов"

    def __str__(self) -> str:
        return self.title_description


class DescriptionImage(models.Model):
    image = models.ImageField(
        verbose_name="Изображение",
        blank=True,
        upload_to="descrp_images/%Y/%m/%d/%H/%M/%S/",
        help_text="Это миниатюрное представление изображения описания.",
    )
    description = models.ForeignKey(
        ProductDescription,
        on_delete=models.CASCADE,
        verbose_name="Описание",
        blank=True,
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self) -> str:
        return self.description.pk
