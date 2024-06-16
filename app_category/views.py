from collections import defaultdict

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from app_category.models import Category
from app_category.serializers import CategorySerializer

from app_products.models import Products


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=False, methods=["get"])
    def lang(self, request, lang=None, *args):
        # Вызываем отдельный метод для получения дерева с переводом
        tree_category = self._get_tree_category(lang)
        return Response(tree_category)

    @action(detail=True, methods=["get"])
    def lang_(self, request, pk=None, lang=None, *args):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # Вызываем отдельный метод для работы с переводом
        response_data = self.process_translation(serializer.data, lang)
        return Response(response_data)

    # Метод представления для получения списка продуктов по категории
    # @action(detail=True, methods=["get"])
    # def products(self, request, pk=None, lang=None, *args):
    #     # Получаем объект категории по её id (pk)
    #     category = self.get_object()

    #     # Получаем все продукты для данной категории и ее подкатегорий
    #     products = self.get_products_by_category(category)

    #     # Применяем пагинацию к результатам запроса
    #     paginator = LimitOffsetPagination()
    #     paginated_products = paginator.paginate_queryset(products, request)

    #     # Сериализуем товары
    #     serializer = ProductsSerializer(paginated_products, many=True)
    #     return paginator.get_paginated_response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        tree_category = self.build_tree(serializer.data)
        return Response(tree_category)

    def build_tree(self, categories, lang=None):
        # defaultdict для автоматического создания пустых списков для детей каждой категории
        # функция для фронта, которая надублирует ему записей (не понятно зачем)
        # и по полочкам разложит вложенность категорий
        # потому что он сам не может.
        category_map = defaultdict(list)
        roots = []

        for category in categories:
            lang_value = (
                category.get("additional_data", {}).get(
                    lang.upper(), category["name_category"]
                )
                if lang
                else category["name_category"]
            )
            if lang_value == "":
                lang_value = category["name_category"]
            category.update(
                {
                    "name_category": lang_value,
                    "title": lang_value,
                    "label": lang_value,
                    "value": lang_value,
                    "key": f"{category['level']}-{category['tree_id']}-{category['id']}",
                    "children": [],
                }
            )

            # Добавление категории в соответствующий словарь
            category_map[category["id"]] = category

            if category["parent"] is None:
                roots.append(category)
            else:
                # Добавление категории как дочерней для ее родителя
                category_map[category["parent"]]["children"].append(category)

        return roots

    def _get_tree_category(self, lang):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        tree_category = self.build_tree(serializer.data, lang)
        return tree_category

    def get_products_by_category(self, category):
        # Получаем все товары, связанные с этой категорией
        products = Products.objects.filter(category=category)

        # Если в категории нет продуктов, рекурсивно получаем продукты из всех подкатегорий
        if not products.exists():
            # Получаем все подкатегории данной категории
            subcategories = category.children.all()

            # Рекурсивно обходим каждую подкатегорию
            for subcategory in subcategories:
                products |= self.get_products_by_category(subcategory)

        return products

    def process_translation(self, data, lang):
        if lang is not None:
            lang = lang.upper()
            additional_data = data.get("additional_data", {})
            if lang in additional_data:
                value_translate = additional_data[lang]
                data_translate = dict(data)
                pass_value = data_translate["name_category"]
                if value_translate:
                    data_translate.update(
                        {
                            "name_category": value_translate,
                            "title": value_translate,
                            "label": value_translate,
                            "value": value_translate,
                        }
                    )
                else:
                    data_translate.update(
                        {
                            "name_category": pass_value,
                            "title": pass_value,
                            "label": pass_value,
                            "value": pass_value,
                        }
                    )
                return data_translate
        return data
