from django import forms

from app_products.models import Products


# TODO Не используется, оставлено как интересное решение
# для вывода древовидной структуры категорий в карточке создания продукта
class ProductAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        choices = []
        for category in self.fields["category"].queryset:
            choices.append(
                (category.id, "".join([" --- " * category.level, category.__str__()]))
            )
        self.fields["category"].choices = choices

    class Meta:
        model = Products
        fields = [
            "name_product",
            "category",
            "price",
            "remaining_goods",
        ]
