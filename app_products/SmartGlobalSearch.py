from django.db.models.functions import Cast
from django.db.models import Q, F, Value, TextField
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity,
)

from rest_framework.views import APIView
from rest_framework.response import Response

from app_category.models import Category
from app_brands.models import Brands
from app_manager_tags.models import Tag

from app_products.serializers_v2 import ProductSerializer
from app_products.ProductsQueryFactory import ProductsQueryFactory

from rest_framework.pagination import LimitOffsetPagination


class ProductSearchPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class SmartGlobalSearchView(APIView):
    """
    Глобальный умный поиск по товарам, категориям и брендам.

    GET-параметры:
    - q (str, required): Поисковый запрос (название товара, категории бренда, характеристики).
    - city (str, optional): Название города для фильтрации по доступности остатков.

    Пример запроса:
        /api/v2/globalsearch/?city=Караганда&q=Диван
    """

    def get(self, request):
        query = request.GET.get("q", "").strip()
        city_name = request.GET.get("city", "").strip()
        if not query:
            return Response(
                {
                    "products": [],
                    "categories": [],
                    "brands": [],
                    "tags": [],
                }
            )

        casted_query = Cast(Value(query), output_field=TextField())
        product_query = SearchQuery(query, config="russian")

        # === Продукты ===
        qs = ProductsQueryFactory.get_base_query()
        qs = ProductsQueryFactory.enrich(qs)

        if city_name:
            qs = qs.filter(stocks__warehouse__city__name_city=city_name)

        products = (
            qs.annotate(
                rank=SearchRank(F("search_vector"), product_query),
                similarity_name=TrigramSimilarity("name_product", casted_query),
            )
            .filter(Q(search_vector=product_query) | Q(similarity_name__gt=0.2))
            .annotate(score=F("rank") + F("similarity_name"))
            .order_by("-score")
            .distinct()
        )

        paginator = ProductSearchPagination()
        paginated_qs = paginator.paginate_queryset(products, request, view=self)

        serialized_products = ProductSerializer(
            paginated_qs, many=True, context={"request": request}
        ).data

        # === Категории ===
        category_vector = SearchVector("name_category", weight="A") + SearchVector(
            "additional_data", weight="B"
        )
        category_query = SearchQuery(query)

        categories = (
            Category.objects.annotate(
                rank=SearchRank(category_vector, category_query),
                similarity=TrigramSimilarity("name_category", casted_query),
                search=category_vector,
            )
            .filter(Q(search=category_query) | Q(similarity__gt=0.2))
            .annotate(score=F("rank") + F("similarity"))
            .order_by("-score")
            .values("id", "name_category", "slug", "additional_data")[:5]
        )

        # === Бренды ===
        brand_vector = SearchVector("name_brand", weight="A") + SearchVector(
            "additional_data", weight="B"
        )
        brand_query = SearchQuery(query)

        brands = (
            Brands.objects.annotate(
                rank=SearchRank(brand_vector, brand_query),
                similarity=TrigramSimilarity("name_brand", casted_query),
                search=brand_vector,
            )
            .filter(Q(search=brand_query) | Q(similarity__gt=0.2))
            .annotate(score=F("rank") + F("similarity"))
            .order_by("-score")
            .values("id", "name_brand", "additional_data")[:5]
        )

        # === Теги ===
        tags = (
            Tag.objects.annotate(similarity=TrigramSimilarity("tag_text", casted_query))
            .filter(similarity__gt=0.2)
            .order_by("-similarity")
            .values("id", "tag_text", "additional_data")[:5]
        )

        return paginator.get_paginated_response(
            {
                "products": serialized_products,
                "categories": list(categories),
                "brands": list(brands),
                "tags": list(tags),
            }
        )
