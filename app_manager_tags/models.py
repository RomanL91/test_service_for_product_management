from django.db import models
from django.core.validators import RegexValidator

from core.mixins import JSONFieldsMixin


class ColorField(models.CharField):
    """Поле для хранения HTML-кода цвета."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 7)
        super().__init__(*args, **kwargs)
        self.validators.append(RegexValidator(r"#[a-f\d]{6}"))


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
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return self.tag_text
