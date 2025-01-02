from django import forms
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType

from app_sales_points.models import Edges
from app_category.models import Category
from app_brands.models import Brands


class EdgesForm(forms.ModelForm):
    object_name = forms.ChoiceField(
        label="Выбор объекта", help_text="Выбор конкретной категории или бренда"
    )  # Используем ChoiceField для динамического выбора

    class Meta:
        model = Edges
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Устанавливаем пустой список по умолчанию
        self.fields["object_name"].choices = []

        # Динамическое заполнение на основе content_type
        content_type_id = self.data.get("content_type") or (
            self.instance.content_type.pk if self.instance.pk else None
        )

        if content_type_id:
            try:
                model_class = ContentType.objects.get(
                    id=int(content_type_id)
                ).model_class()
                objects = model_class.objects.all()

                if model_class == Category:
                    # Выставляем ID и имя категории
                    self.fields["object_name"].choices = [
                        (obj.pk, obj.name_category) for obj in objects
                    ]
                elif model_class == Brands:
                    # Выставляем ID и имя бренда
                    self.fields["object_name"].choices = [
                        (obj.pk, obj.name_brand) for obj in objects
                    ]
            except (ValueError, ContentType.DoesNotExist) as e:
                # Добавляем сообщение об ошибке в админку
                messages.error(
                    self.request,
                    f"Ошибка: не удалось загрузить объекты для content_type {content_type_id}. Причина: {str(e)}",
                )
                # В случае ошибки очищаем выбор
                self.fields["object_name"].choices = []

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Присваиваем object_id значение выбранного object_name
        object_id = self.cleaned_data.get("object_name")
        if object_id:
            instance.object_id = object_id

        if commit:
            instance.save()
        return instance
