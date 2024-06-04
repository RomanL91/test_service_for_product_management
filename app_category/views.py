from collections import defaultdict

from django.db.models import Q

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from core import settings

from app_category.models import Category
from app_category.serializers import CategorySerializer

from app_products.models import Products
from app_products.serializers import ProductsSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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

    @action(detail=False, methods=["get"])
    def en(self, request, pk=None, *args):
        tree_category = self._get_tree_category(settings.LANG_EN)
        return Response(tree_category)

    @action(detail=False, methods=["get"])
    def kz(self, request, pk=None, *args):
        tree_category = self._get_tree_category(settings.LANG_KZ)
        return Response(tree_category)

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        # Получаем объект категории по её id (pk)
        category = self.get_object()

        # Получаем все товары, связанные с этой категорией
        products = Products.objects.filter(category=category)

        # Если в категории нет продуктов, получаем продукты из всех подкатегорий
        if not products.exists():
            # Получаем все подкатегории данной категории
            subcategories = category.children.all()
            # Создаем Q-объект, который будет объединять все подкатегории
            q_objects = Q()
            for subcategory in subcategories:
                # Добавляем к Q-объекту условие для каждой подкатегории
                q_objects |= Q(category=subcategory)
            
            # Фильтруем продукты по Q-объекту    
            products = Products.objects.filter(q_objects)

        # Применяем пагинацию к результатам запроса
        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(products, request)

        # Сериализуем товары
        serializer = ProductsSerializer(paginated_products, many=True)

        return paginator.get_paginated_response(serializer.data)
