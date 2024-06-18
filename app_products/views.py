from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response

from app_products.models import Products
from app_category.models import Category
from app_products.serializers import ProductsListSerializer, ProductsDetailSerializer


class ProductsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsListSerializer
    lookup_field = "slug_prod"

    def retrieve(self, request, slug_prod=None, *args, **kwargs):
        instance = self.get_object_by_slug(slug_prod)
        # Для представления instance изменяем класс серализатора
        self.serializer_class = ProductsDetailSerializer
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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

    def lang_(self, request, lang=None, slug_prod=None, *args, **kwargs):
        instance = self.get_object_by_slug(slug_prod)
        self.serializer_class = ProductsDetailSerializer
        serializer = self.get_serializer(instance)
        response_data = self.process_translation([serializer.data], lang, True)
        return Response(response_data)

    def filter_by_cat(self, request, slug_cat=None, *args, **kwargs):
        products_queryset = self.get_products_by_category(slug_cat)
        serializer = self.get_serializer(products_queryset, many=True)
        return Response(serializer.data)

    def process_translation(self, data, lang, detail=False):
        if lang is not None:
            lang = lang.upper()
            data_translate = []
            for el in data:
                additional_data = el.get("additional_data", {})

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
                pass
                # category_product = data_translate[0]["category"]
                # category_product = self.fields_product_translate(
                #     category_product, "name_category", lang
                # )

                # brand_product = data_translate[0]["brand"]
                # brand_product = self.fields_product_translate(
                #     brand_product, "name_brand", lang
                # )

                # related_product = data_translate[0]["related_product"]
                # related_product = self.related_product_translate_field(
                #     related_product, lang
                # )
                return data_translate[0]
            return data_translate
        return data

    def related_product_translate_field(self, list_related_product, lang):
        return self.process_translation(list_related_product, lang)

    def fields_product_translate(self, field, name_field, lang):
        traslate_data = field.get("additional_data", {})
        traslate_value = traslate_data.get(lang, field[name_field])

        if traslate_value != "":
            field[name_field] = traslate_value

        return field

    def get_object_by_slug(self, slug):
        return get_object_or_404(self.get_queryset(), slug=slug)

    def get_products_by_category(self, slug_cat):
        # Получаем все товары, связанные с этой категорией
        products_queryset = self.queryset.filter(category__slug=slug_cat)

        # Если в категории нет продуктов, рекурсивно получаем продукты из всех подкатегорий
        if not products_queryset.exists():
            category = get_object_or_404(Category, slug=slug_cat)

            # Получаем все подкатегории данной категории
            subcategories = category.children.all()

            # Рекурсивно обходим каждую подкатегорию
            for subcategory in subcategories:
                products_queryset |= self.get_products_by_category(subcategory.slug)

        return products_queryset
