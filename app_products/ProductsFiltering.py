from decimal import Decimal, InvalidOperation

import django_filters as df

from django import forms
from django.db.models import Min, Q
from django_filters.widgets import CSVWidget

from app_products.models import Products
from app_category.models import Category


class CharInFilter(df.BaseInFilter, df.CharFilter):
    """brand=apple,samsung — lookup IN со строками."""

    pass


class PriceRangeFilter(df.CharFilter):
    """
    Фильтрует товары по min(stock.price) в заданном диапазоне.
    Форматы: 100..5000000   100..   ..5000000
    """

    SEP = ".."

    def _bounds(self, raw: str):
        """
        Возвращает (lower, upper) как Decimal | None.
        Разбираем строки '100..500', '100..', '..500', '100'.
        """
        lower, upper = None, None
        parts = raw.split(self.SEP, 1)
        if len(parts) == 2:  # есть разделитель ..
            lower, upper = parts
        else:  # одиночное число → lower-bound
            lower = parts[0]

        def to_decimal(s):
            try:
                return Decimal(s) if s else None
            except (InvalidOperation, TypeError):
                return None

        return to_decimal(lower), to_decimal(upper)

    def filter(self, qs, value):
        if not value:
            return qs

        lower, upper = self._bounds(value)

        # минимальная НЕ нулевая цена товара
        qs = qs.annotate(
            min_price=Min(
                "stocks__price",
                filter=Q(stocks__price__gt=0),  # игнорируем 0 / NULL
            )
        ).exclude(min_price__isnull=True)

        if lower is not None:
            qs = qs.filter(min_price__gte=lower)
        if upper is not None:
            qs = qs.filter(min_price__lte=upper)
        return qs


class ProductsFilter(df.FilterSet):
    #
    #  1. Несколько брендов: ?brand=apple,samsung
    #
    brand = CharInFilter(
        label="Бренд",
        field_name="brand__name_brand",
        lookup_expr="in",
        widget=CSVWidget(attrs={"placeholder": "name_brand: ?brand=apple,samsung"}),
    )
    #
    #  2. Категория + её потомки по slug: ?category=laptops
    #
    category = df.CharFilter(
        label="Категория",
        method="filter_category",
        widget=forms.TextInput(attrs={"placeholder": "slug: ?category=laptops"}),
    )

    def filter_category(self, qs, name, value):

        cat = Category.objects.filter(slug=value).first()
        if not cat:
            return qs.none()
        return qs.filter(category__in=cat.get_descendants(include_self=True))

    #
    #  3. Характеристики (динамически): ?spec=color:red,size:15
    #
    spec = df.CharFilter(
        label="Характеристики",
        method="filter_specs",
        widget=forms.TextInput(
            attrs={
                "placeholder": "key:val|val,key:val -> ?spec=color:red,size:15|16|20"
            }
        ),
    )

    def filter_specs(self, qs, name, value):
        """
        Ожидаем строку вида color:red,size:15|16|17
        Каждая пара = обязательное условие AND, внутри пары несколько значений через |
        """
        for pair in filter(None, value.split(",")):
            key, vals = pair.split(":")
            vals = vals.split("|")
            qs = qs.filter(
                specifications__name_specification__name_specification__iexact=key,
                specifications__value_specification__value_specification__in=vals,
            )
        return qs

    #
    #  4. Диапазон цен
    #
    price = PriceRangeFilter(
        label="Диапазон цены",
        widget=forms.TextInput(
            attrs={"placeholder": "?price=100..500, 100.., ..500, 100"}
        ),
    )

    class Meta:
        model = Products
        fields = []
