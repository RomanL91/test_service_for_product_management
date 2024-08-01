from rest_framework import viewsets
from rest_framework.response import Response

from django.db.models import Min, Max

from app_sales_points.models import Stock, City
from app_category.models import Category
from app_products.models import Products
from app_sales_points.serializers import (
    StockSerializer,
    PriceRangeByCitySerializer,
    CitySerializer,
)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class StocksViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.select_related(
        "warehouse__city", "product__category"
    ).all()
    serializer_class = StockSerializer

    def filter_by_prod(self, request, prod_pk, city_pk=None, *args, **kwargs):
        stocks = Stock.objects.filter(product_id=prod_pk, warehouse__city=city_pk)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)

    def get_prices_by_category(self, request, cat_pk):
        # Получаем категорию и все её подкатегории
        descendant_categories = (
            Category.objects.get(pk=cat_pk)
            .get_descendants(include_self=True)
            .values_list("id", flat=True)
        )

        # Получаем продукты из этих категорий
        product_ids = Products.objects.filter(
            category_id__in=descendant_categories
        ).values_list("id", flat=True)

        # Получаем цены на эти продукты, группируя по городам складов
        prices = (
            Stock.objects.filter(product_id__in=product_ids)
            .select_related("warehouse__city")
            .values("warehouse__city__name_city")
            .annotate(MinPrice=Min("price"), MaxPrice=Max("price"))
            .order_by("warehouse__city__name_city")
        )

        # Сериализуем данные
        serializer = PriceRangeByCitySerializer(prices, many=True)
        return Response(serializer.data)
