from django import forms

from django.db import models

from flat_json_widget.widgets import FlatJsonWidget


class JsonDocumentForm(forms.ModelForm):
    class Meta:
        widgets = {"additional_data": FlatJsonWidget}


class JSONFieldsMixin(models.Model):
    def default_additional_data():
        return {"RU": "", "EN": "", "KZ": ""}

    additional_data = models.JSONField(
        verbose_name="Дополнительные данные",
        help_text="""Данные поля предназначены для перевода на другие языки.<br>
                        Можно добавить сколько угодно переводов.""",
        blank=True,
        null=True,
        default=default_additional_data(),
    )

    class Meta:
        abstract = True
