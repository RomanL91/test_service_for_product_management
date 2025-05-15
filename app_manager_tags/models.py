from django.db import models
from django.contrib.postgres.indexes import GinIndex

from django.core.validators import RegexValidator

from core.mixins import JSONFieldsMixin

from core.TranslationDecorator import register_for_translation


class ColorField(models.CharField):
    """Поле для хранения HTML-кода цвета."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 7)
        super().__init__(*args, **kwargs)
        self.validators.append(RegexValidator(r"#[a-f\d]{6}"))


@register_for_translation("tag_text", "additional_data")
class Tag(JSONFieldsMixin, models.Model):
    tag_text = models.CharField(max_length=10, verbose_name="Текст тега")
    font_color = ColorField(
        verbose_name="Цвет шрифта",
        default="#FF0000",
        blank=True,
    )
    fill_color = ColorField(
        verbose_name="Цвет шрифта",
        default="#FF0000",
        blank=True,
    )

    class Meta:
        indexes = [
            GinIndex(
                fields=["tag_text"],
                name="trgm_idx_tag_text",
                opclasses=["gin_trgm_ops"],
            ),
        ]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return self.tag_text
