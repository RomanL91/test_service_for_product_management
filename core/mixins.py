from django import forms

from django.db import models

from flat_json_widget.widgets import FlatJsonWidget

from django.utils.html import format_html
from django.contrib.admin.widgets import AdminFileWidget


class JsonDocumentForm(forms.ModelForm):
    class Meta:
        widgets = {
            "additional_data": FlatJsonWidget,
            "additional_data_to_desc": FlatJsonWidget,
        }


class DefaultAdditionalDataMixin:
    @staticmethod
    def default_additional_data():
        return {
            # "RU": "",
            "EN": "",
            "KZ": "",
        }


class JSONFieldsMixin(DefaultAdditionalDataMixin, models.Model):
    additional_data = models.JSONField(
        verbose_name="Дополнительные данные",
        help_text="""Данные поля предназначены для перевода на другие языки.<br>
                        Можно добавить сколько угодно переводов.""",
        blank=True,
        null=True,
        # Используем метод из базового миксина
        default=DefaultAdditionalDataMixin.default_additional_data,
    )

    class Meta:
        abstract = True


class JSONFieldsDescMixin(DefaultAdditionalDataMixin, models.Model):
    additional_data_to_desc = models.JSONField(
        verbose_name="Дополнительные данные для перевода описания",
        help_text="""Данные поля предназначены для перевода на другие языки.<br>
                        Можно добавить сколько угодно переводов.""",
        blank=True,
        null=True,
        # Используем метод из базового миксина
        default=DefaultAdditionalDataMixin.default_additional_data,
    )

    class Meta:
        abstract = True


class SlugModelMixin(models.Model):
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True, verbose_name="URL"
    )

    class Meta:
        abstract = True


class CustomAdminFileWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if hasattr(value, "url"):
            result.append(
                f"""<a href="{value.url}" target="_blank">
                      <img 
                        src="{value.url}" alt="{value}" 
                        width="100" height="100"
                        style="object-fit: cover;"
                      />
                    </a>"""
            )
        result.append(super().render(name, value, attrs, renderer))
        return format_html("".join(result))
