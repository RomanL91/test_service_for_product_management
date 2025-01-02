from datetime import date
from django.db.models import Avg, Count, Prefetch

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from app_products.models import Products, ProductImage
from app_sales_points.models import Edges
from app_sales_points.models import Stock
from app_specifications.models import Specifications

from app_products.serializers_v2 import ProductSerializer


class ProductsPagination(LimitOffsetPagination):
    default_limit = 10  # Переопределение значения limit
    max_limit = 100  # Максимальный размер страницы


class ProductsViewSet_v2(ReadOnlyModelViewSet):
    """
    Представление только для чтения продуктов с аннотированной информацией.
    """

    queryset = (
        Products.objects.select_related(
            "category__parent",
            "brand",
        )
        .prefetch_related(
            "tag_prod",
            Prefetch(
                "specifications",
                queryset=Specifications.objects.select_related(
                    "name_specification", "value_specification"
                ),
                to_attr="prefetched_specifications",
            ),
            Prefetch(
                "stocks",
                queryset=Stock.objects.select_related(
                    "warehouse__city",
                ),
                to_attr="prefetched_stocks",
            ),
            Prefetch(
                "category__edges",
                queryset=Edges.objects.filter(
                    expiration_date__gt=date.today(), is_active=True
                ).select_related("city_from", "city_to"),
                to_attr="related_edges",
            ),
            Prefetch(
                "brand__edges",
                queryset=Edges.objects.filter(
                    expiration_date__gt=date.today(), is_active=True
                ).select_related("city_from", "city_to"),
                to_attr="related_edges",
            ),
            Prefetch(
                "productimage_set",  # Связь с изображениями продукта
                queryset=ProductImage.objects.select_related("product"),
                to_attr="images",  # Сохраняем изображения в поле `images`
            ),
        )
        .annotate(
            avg_rating=Avg("review__rating"),  # Средний рейтинг
            reviews_count=Count("review", distinct=True),  # Количество отзывов
        )
    )
    serializer_class = ProductSerializer
    pagination_class = ProductsPagination
    lookup_field = "slug"  # Указываем поле для поиска
