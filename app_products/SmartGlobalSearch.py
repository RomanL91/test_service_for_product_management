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

        # === Продукты ===
        product_vector = (
            SearchVector("name_product", weight="A", config="russian")
            + SearchVector("additional_data", weight="B", config="russian")
            + SearchVector("vendor_code", weight="C", config="russian")
        )
        product_query = SearchQuery(query, config="russian")

        qs = ProductsQueryFactory.get_base_query()
        qs = ProductsQueryFactory.enrich(qs)

        if city_name:
            qs = qs.filter(stocks__warehouse__city__name_city=city_name)

        qs = qs.annotate(
            rank=SearchRank(product_vector, product_query),
            similarity_name=TrigramSimilarity("name_product", casted_query),
            similarity_spec_name=TrigramSimilarity(
                "specifications__name_specification__name_specification", casted_query
            ),
            similarity_spec_value=TrigramSimilarity(
                "specifications__value_specification__value_specification", casted_query
            ),
            search=product_vector,
        )

        # Фильтрация по основному вектору + характеристикам
        products = (
            qs.filter(
                Q(search=product_query)
                | Q(similarity_name__gt=0.2)
                | Q(similarity_spec_name__gt=0.2)
                | Q(similarity_spec_value__gt=0.2)
            )
            .annotate(
                score=F("rank")
                + F("similarity_name")
                + F("similarity_spec_name")
                + F("similarity_spec_value")
            )
            .order_by("-score")[:8]
        )

        serialized_products = ProductSerializer(
            products, many=True, context={"request": request}
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
            .values("id", "name_category", "slug")[:5]
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
            .values("id", "name_brand")[:5]
        )

        # === Теги ===
        tags = (
            Tag.objects.annotate(similarity=TrigramSimilarity("tag_text", casted_query))
            .filter(similarity__gt=0.2)
            .order_by("-similarity")
            .values("id", "tag_text")[:5]
        )

        return Response(
            {
                "products": serialized_products,
                "categories": list(categories),
                "brands": list(brands),
                "tags": list(tags),
            }
        )
