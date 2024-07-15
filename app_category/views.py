from collections import defaultdict

from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response

from app_category.models import Category
from app_category.serializers import CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug_cat"

    def retrieve(self, request, slug_cat=None, *args, **kwargs):
        instance = self.get_object_by_slug(slug_cat)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        tree_category = self.build_tree(serializer.data)
        return Response(tree_category)

    def build_tree(self, categories):
        category_map = defaultdict(list)
        roots = []

        for category in categories:
            name_category = category["name_category"]
            category.update(
                {
                    "name_category": name_category,
                    "title": name_category,
                    "label": name_category,
                    "value": name_category,
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

    def get_object_by_slug(self, slug):
        return get_object_or_404(self.get_queryset(), slug=slug)

    def subcategories(self, request, slug_cat=None):
        category = self.get_object_by_slug(slug_cat)
        subcategories = category.get_descendants(include_self=False)
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)
