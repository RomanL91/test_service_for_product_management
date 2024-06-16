from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from app_products.models import Products
from app_products.serializers import ProductsListSerializer, ProductsDetailSerializer


class ProductsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Для представления instance изменяем класс серализатора
        self.serializer_class = ProductsDetailSerializer
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def lang(self, request, lang=None, *args, **kwargs):
        products_queryset = self.get_queryset()
        page = self.paginate_queryset(products_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data_translate = self.process_translation(serializer.data, lang)
            return self.get_paginated_response(data_translate)
        serializer = self.get_serializer(products_queryset, many=True)
        data_translate = self.process_translation(serializer.data, lang)
        return Response(data_translate)

    @action(detail=True, methods=["get"])
    def lang_(self, request, lang=None, *args, **kwargs):
        instance = self.get_object()
        self.serializer_class = ProductsDetailSerializer
        serializer = self.get_serializer(instance)
        response_data = self.process_translation([serializer.data], lang, True)
        return Response(response_data)

    def process_translation(self, data, lang, detail=False):
        if lang is not None:
            lang = lang.upper()
            data_translate = []
            for el in data:
                pass_value = el["name_product"]
                additional_data = el.get("additional_data", {})
                el.update(
                    {
                        "name_product": pass_value,
                    }
                )
                if lang in additional_data:
                    value_translate = additional_data[lang]

                    if value_translate:
                        el.update(
                            {
                                "name_product": value_translate,
                            }
                        )
                data_translate.append(el)
            if detail:
                related_product = data_translate[0]["related_product"]
                translate_related_product = self.process_translation(related_product, lang)
                related_product = translate_related_product
                return data_translate[0]
            return data_translate
        return data
