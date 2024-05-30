from rest_framework import viewsets
from rest_framework.response import Response

from app_category.models import Category

from app_category.serializers import CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            tree_category = build_tree(serializer.data)

            return self.get_paginated_response(tree_category)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def build_tree(categories):
    category_map = {}
    roots = []

    for category in categories:
        category['children'] = []
        category_map[category['id']] = category

        if category['parent'] is None:
            roots.append(category)
        else:
            parent = category_map[category['parent']]
            parent['children'].append(category)

    return roots