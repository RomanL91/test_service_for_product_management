from typing import Dict, Any, Generator

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import viewsets, pagination
from rest_framework.decorators import action

from core import settings

from app_products.models import Products
from app_products.serializers import ProductsSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer

    @action(detail=False, methods=["get"])
    def en(self, request: Request, *args, **kwargs) -> Response:
        return self.paginate_and_translate(request, settings.LANG_EN)

    @action(detail=True, methods=["get"])
    def en_(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        translated_data = self.translate_object(serializer.data, settings.LANG_EN)
        return Response(translated_data)

    @action(detail=False, methods=["get"])
    def kz(self, request: Request, *args, **kwargs) -> Response:
        return self.paginate_and_translate(request, settings.LANG_KZ)

    @action(detail=True, methods=["get"])
    def kz_(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        translated_data = self.translate_object(serializer.data, settings.LANG_KZ)
        return Response(translated_data)

    def paginate_and_translate(self, request, lang: str) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        # paginator = pagination.PageNumberPagination()
        paginator = pagination.LimitOffsetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_queryset, many=True)
        translated_data = self.translate_queryset(serializer.data, lang)
        return paginator.get_paginated_response(translated_data)

    def translate_queryset(
        self, queryset: Dict[str, Any], lang: str
    ) -> Generator[Dict[str, Any], None, None]:
        for item in queryset:
            translated_item = {}
            for key, value in item.items():
                if key == "category":
                    if value is not None:
                        translate_value = value["additional_data"].get(lang, "")
                        if translate_value != "":
                            value["name_category"] = translate_value
                elif key == "brand":
                    if value is not None:
                        translate_value = value["additional_data"].get(lang, "")
                        if translate_value != "":
                            value["name_brand"] = translate_value
                elif key == "name_product":
                    if value is not None:
                        translate_value = item["additional_data"].get(lang, "")
                        if translate_value != "":
                            value = translate_value
                elif key == "related_products":
                    value = self.translate_queryset(value, lang)
                translated_item[key] = value
            yield translated_item

    def translate_object(self, obj: Any, lang: str) -> Any:
        if isinstance(obj, list):
            return [self.translate_object(item, lang) for item in obj]

        translated_obj = {}
        for key, value in obj.items():
            if key == "category" or key == "brand":
                if value is not None:
                    translate_value = value.get("additional_data", {}).get(lang, "")
                    if translate_value != "":
                        value[f"name_{key}"] = translate_value
            elif key == "name_product":
                if value is not None:
                    translate_value = obj.get("additional_data", {}).get(lang, "")
                    if translate_value != "":
                        value = translate_value
            elif key == "related_products":
                value = self.translate_object(value, lang)
            translated_obj[key] = value
        return translated_obj
