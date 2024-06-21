from collections import defaultdict

from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response

from app_category.models import Category
from app_category.serializers import CategorySerializer

from core.lang_utils import TranslateManager


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug_cat"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translate_manager = TranslateManager(self)

    def retrieve(self, request, slug_cat=None, lang=None, *args, **kwargs):
        instance = self.get_object_by_slug(slug_cat)
        serializer = self.get_serializer(instance)
        if lang is not None:
            self.translate_manager.translate_instance(instance, "name_category", lang)
        return Response(serializer.data)

    def list(self, request, lang=None, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        if lang is not None:
            self.translate_manager.translate_queryset(queryset, "name_category", lang)
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

    def get_object_by_slug(self, slug):
        return get_object_or_404(self.get_queryset(), slug=slug)
