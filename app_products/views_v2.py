from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from app_products.serializers_v2 import ProductSerializer

from app_products.ProductsQueryFactory import ProductsQueryFactory


class ProductsPagination(LimitOffsetPagination):
    default_limit = 10  # Переопределение значения limit
    max_limit = 100  # Максимальный размер страницы


class ProductsViewSet_v2(ReadOnlyModelViewSet):
    """
    Представление только для чтения продуктов с аннотированной информацией.
    """

    queryset = ProductsQueryFactory.get_all_details()
    serializer_class = ProductSerializer
    pagination_class = ProductsPagination
    lookup_field = "slug"  # Указываем поле для поиска

    @action(detail=False, methods=["get"], url_path="filter_by_ids")
    def filter_by_ids(self, request, *args, **kwargs):
        ids_param = request.query_params.get("ids")
        if not ids_param:
            return Response({"detail": "No 'ids' param"}, status=400)
        try:
            ids_list = [int(pk) for pk in ids_param.split(",") if pk.strip()]
        except ValueError:
            return Response({"detail": "Invalid 'ids' format"}, status=400)

        queryset = self.filter_queryset(self.get_queryset().filter(pk__in=ids_list))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
