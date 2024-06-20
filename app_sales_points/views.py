from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response

from app_sales_points.models import Stock
from app_products.models import Products
from app_sales_points.serializers import StockSerializer


class StocksViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    def lang(self, request, lang=None, *args, **kwargs):
        stocks_queryset = self.get_queryset()
        serializer = self.get_serializer(stocks_queryset, many=True)
        data_translate = self.translate_data(serializer.data, lang)
        return Response(data_translate)

    def filter_by_prod(self, request, slug_prod=None, *args, **kwargs):
        product = get_object_or_404(Products, slug=slug_prod)
        stocks = Stock.objects.filter(product=product)
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)

    def translate_data(self, data, lang):
        if lang is not None:
            lang = lang.upper()
            for el in data:
                el["warehouse"] = self.fields_translate(
                    el["warehouse"], "name_warehouse", lang
                )
                el["warehouse"]["city"] = self.fields_translate(
                    el["warehouse"]["city"], "name_city", lang
                )
        return data

    def fields_translate(self, field, name_field, lang):
        traslate_data = field.get("additional_data", {})
        traslate_value = traslate_data.get(lang, field[name_field])

        if traslate_value != "":
            field[name_field] = traslate_value

        return field
