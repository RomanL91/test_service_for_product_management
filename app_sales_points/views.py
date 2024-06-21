from rest_framework import viewsets
from rest_framework.response import Response

from app_sales_points.models import Stock
from app_sales_points.serializers import StockSerializer

from core.lang_utils import TranslateManager


class StocksViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translate_manager = TranslateManager(self)

    def filter_by_prod(
        self, request, prod_pk, city_pk=None, lang=None, *args, **kwargs
    ):
        stocks = Stock.objects.filter(product_id=prod_pk, warehouse__city=city_pk)
        if lang is not None:
            self.translate_data(stocks, lang)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)

    def translate_data(self, data, lang):
        for el in data:
            el.warehouse = self.translate_manager.translate_instance(
                el.warehouse, "name_warehouse", lang
            )
            el.warehouse.city = self.translate_manager.translate_instance(
                el.warehouse.city, "name_city", lang
            )
